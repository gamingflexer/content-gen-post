# Content Generation and Summarization Application

## Introduction
This application is designed to automate the process of content generation and summarization. It scrapes content from specified URLs, generates summaries, and creates PDF documents for various content types such as daily news posts, weekly summaries, and rephrased articles. The application leverages advanced NLP models and provides a user-friendly interface through Gradio for easy interaction.

## Setup Instructions

### Dependencies Installation
First, ensure you have Python installed on your system. Then, install the required dependencies by running:
```
pip install -r src/requirements.txt
```

### Environment Setup
Copy the `.env.example` file in the `src` directory to `.env` and fill in the necessary API keys:
```
cp src/.env.example src/.env
```

### Launching the Application
To start the application, navigate to the `src` directory and run:
```
python app.py
```
This will launch a Gradio interface accessible via a web browser.

## Application Architecture

The application follows a modular architecture, consisting of several components:

- **Content Scraping**: Modules in `src/content_maker.py` and `src/srcapper` handle scraping content from provided URLs and PDF documents.
- **Summarization and Content Generation**: Leveraging NLP models, the application summarizes scraped content and generates new content based on user inputs.
- **PDF Generation**: Summarized content and generated posts are converted into PDF format for easy distribution.
- **Gradio Interface**: `src/app.py` includes a Gradio web interface that allows users to interact with the application through a web browser, performing tasks like content scraping, summarization, and PDF generation.

## Usage Examples

### Generating a Daily News Post
1. Navigate to the "Daily Post of the Day" tab.
2. Enter URLs in the textbox or upload PDF files.
3. Click "Start" to generate a daily news post.

### Summarizing Weekly News
1. Go to the "Weekly Summarised POST (LAST)" tab.
2. Click "Start" to retrieve and summarize the past week's news.

### Rephrasing an Article
1. Select the "Pdf article Rephrasing" tab.
2. Upload a PDF file to be rephrased.
3. The application will generate a rephrased version of the article.

## Troubleshooting

- **Issue**: Application does not start.
  - **Solution**: Ensure all dependencies are installed and the `.env` file is correctly set up.
- **Issue**: Gradio interface is not accessible.
  - **Solution**: Check if the application is running and listen to the correct port as specified in `app.py`.
- **Issue**: Error during content scraping.
  - **Solution**: Verify the URLs are accessible and valid. Ensure the application has internet access.

For more detailed information on troubleshooting, refer to the application logs and documentation.
