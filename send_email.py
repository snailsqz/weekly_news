from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv
load_dotenv()

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
    with open("summarynews.txt", "r", encoding="utf-8") as file:
        content = file.read()
    to_email = input("Enter destination email: ").strip()
    result = send_email("Weekly Economy News!!", content, to_email)
    print(result)

if __name__ == "__main__":
    main()