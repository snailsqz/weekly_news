import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
import random
import os
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
#email,app password,huggingfaceapikey
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

def scrape_news():
    url = "https://www.cnbc.com/economy/" #You can change to any topic you want on cnbc.com
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_data = []
        
        # Try different selectors (CNBC might change their layout)
        articles = soup.select('.Card-card')
        if not articles:
            articles = soup.select('.Card')
        if not articles:
            articles = soup.select('article')
            
        print(f"Found {len(articles)} articles")
        
        # Process only the first 3 articles you can add more than that
        for i, article in enumerate(articles[:3]):
            if i >= 3:
                break
                
            # Try different ways to find the headline
            headline_tag = article.select_one('.Card-title')
            if not headline_tag:
                headline_tag = article.select_one('a[data-test="Card-title"]')
            if not headline_tag:
                headline_tag = article.select_one('h3')
            if not headline_tag:
                headline_tag = article.select_one('a')
                
            if not headline_tag:
                print(f"Couldn't find headline for article {i+1}")
                continue

            # Get title and link
            title = headline_tag.get_text(strip=True)
            link = None
            
            if headline_tag.name == 'a' and headline_tag.has_attr('href'):
                link = headline_tag['href']
            else:
                link_tag = headline_tag.find('a')
                if link_tag and link_tag.has_attr('href'):
                    link = link_tag['href']
                else:
                    link_tag = article.find('a')
                    if link_tag and link_tag.has_attr('href'):
                        link = link_tag['href']
            
            if not link:
                print(f"Couldn't find link for article: {title}")
                continue
                
            if not link.startswith("http"):
                link = "https://www.cnbc.com" + link
                
            print(f"Processing article {i+1}: {title}")
            print(f"Link: {link}")
            
            # Add a delay to avoid getting blocked
            time.sleep(random.uniform(1, 3))
            
            # Get article content
            try:
                article_res = requests.get(link, headers=headers, timeout=10)
                article_res.raise_for_status()
                article_soup = BeautifulSoup(article_res.text, 'html.parser')
                
                # Try different selectors for article content
                paragraphs = article_soup.select('.ArticleBody-articleBody p')
                if not paragraphs:
                    paragraphs = article_soup.select('.RenderKeyPoints-list li')
                if not paragraphs:
                    paragraphs = article_soup.select('article p')
                if not paragraphs:
                    paragraphs = article_soup.select('.article-body p')
                    
                article_text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                
                if not article_text:
                    print(f"No article text found for: {title}")
                    article_text = "Could not extract article content. Please check the link for full details."
                
                # Create formatted article data
                news_item = f" {title}\n{article_text}\n\n{'-'*60}"
                news_data.append(news_item)
                print(f"Successfully processed article {i+1}")
                
            except Exception as e:
                print(f"Error processing article content: {e}")
                news_data.append(f" {title}\nError retrieving article content.\n\n{'-'*60}")
            
        return '\n\n'.join(news_data)
        
    except Exception as e:
        print(f"Error scraping news: {e}")
        return f"Error scraping news: {e}"

def summarize_news(raw_text):
    try:
        API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an economic news summarizer that can explain content in an easy-to-understand way, with a casual, friendly style, like a friend telling a story – easy to read and relax with."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following economic news in a simple, conversational style without headings or numbering, Also, make sure to include a response to the question Im currently investing in US stocks, how will this affect me?: \n\n{raw_text}"
                }
            ],
            "model": "deepseek/deepseek-v3-0324",
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Status Code: {response.status_code}")
            print(f"Raw Text: {response.text}")
            return "Error summarizing news."

        result = response.json()
        message_content = result["choices"][0]["message"]["content"]
        return message_content.strip()

    except Exception as e:
        print(f"Error in summarizing: {e}")
        return f"Error summarizing news: {e}"

def clean_summary(text):
    # delete **Bold** and *Italic*
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # delete chinese text (Unicode Chinese range)
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=6)
    date_range = f"{start_date.day} - {end_date.day} {end_date.strftime('%B %Y')}"
    
    title = f"📊Weekly Economy News ({date_range})"
    footer="This summary is generated by AI for informational purposes only and should not be considered financial or investment advice. Please use your own judgment before making any decisions."

    full_text = f"{title}\n\n{text.strip()}\n\n{footer}"
    return full_text

def send_email(subject, body, to_email):
    try:
        from_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        
        if not from_email or not password:
            print("Email credentials not found in environment variables")
            return "Email credentials missing. Please check your .env file."
            
        if isinstance(body, dict): 
            body = str(body)
            
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            return "Email sent successfully!"
    except Exception as e:
        print(f"Error sending email: {e}")
        return f"Error sending email: {e}"


def main():
    print("Starting news scraping...")
    news_text = scrape_news()
    
    if not news_text or "Error" in news_text:
        print("Failed to scrape news or no news found.")
        return

    with open("news.txt", "w", encoding="utf-8") as f:
        f.write(news_text)
    print("save to news.txt")
    
    print("\nScraping completed! Now summarizing...")
    
    summary = summarize_news(news_text)
    
    if not summary or "Error" in summary:
        print("Failed to summarize news.")
        return
    
    summary = clean_summary(summary)
        
    with open("summarynews.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("save to summarynews.txt")
    
    print("\nSummary created!")
    print("\n--- SUMMARY ---")
    print(summary)
    print("---------------\n")
    
    send_option = input("Do you want to send this summary via email? (yes/no): ").lower().strip()
    if send_option in ['yes', 'y']:
        to_email = input("Enter destination email: ").strip()
        result = send_email("Weekly Economy News!!", summary, to_email)
        print(result)
    else:
        print("Email not sent. Program completed.")

if __name__ == "__main__":
    main()