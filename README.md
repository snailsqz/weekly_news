# AI-Powered Economic News Summarizer & Emailer

## Project Overview

This project automates the process of staying informed about the latest economic news. It uses web scraping to gather news articles from CNBC, leverages a Hugging Face API to summarize the content with AI, cleans the summarized text, and then sends a concise news digest via email.

## Key Features

* **Automated News Aggregation:** Scrapes economic news from predefined or user-specified web sources.
* **AI-Powered Summarization:** Utilizes Hugging Face's NLP models to generate concise and relevant summaries of news articles.
* **Text Cleaning:** Implements text processing techniques to refine the summaries, removing unnecessary characters or formatting for better readability.
* **Email Notifications:** Delivers the cleaned summaries directly to your inbox, providing a convenient way to stay updated.
* **Configurable:** (Optional: Add this if you plan to make it configurable) Allows users to customize news sources, summarization parameters, and email settings.

## How It Works

1.  **Web Scraping:** The system fetches the latest economic news articles from CNBC/Economy.
2.  **Content Extraction:** Relevant text content is extracted from the scraped web pages.
3.  **AI Summarization:** The extracted text is sent to a Hugging Face API endpoint, where a pre-trained language model generates a summary.
4.  **Text Cleaning:** The generated summary undergoes a cleaning process to ensure clarity and remove any artifacts from the summarization or scraping process.
5.  **Email Dispatch:** The final, cleaned summary is formatted and sent as an email to the configured recipient(s).

## Contributing

Contributions are welcome! If you have suggestions for improvements or want to contribute code, please feel free to:

1.  Fork the Project
2.  Create your Feature Branch
3.  Commit your Changes
4.  Push to the Branch
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

* [Hugging Face](https://huggingface.co/) for their incredible NLP models and API.


