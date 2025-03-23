## News Sentiment Analyzer
Welcome to the News Sentiment Analyzer! This repository contains an application that extracts news articles for a specific company, analyzes their sentiment, identifies key topics, and provides insightful summaries. Additionally, it generates audio summaries in Hindi using Google Cloud Text-to-Speech (TTS). The application is deployed on Hugging Face Spaces for easy access and scalability.

This guide will provide step-by-step instructions on setting up, running, and using the application, along with insights into the underlying architecture and functionality.

### Features
- News Extraction
The application scrapes news articles for the specified company from Economic Times using BeautifulSoup.

- Sentiment Analysis
Sentiment analysis of news articles is performed using pre-trained models from Hugging Face. Each article is classified as Positive, Negative, or Neutral.

- Topic Extraction
Using Hugging Face topic classification models, the application identifies common themes across articles.

- Audio Summarization
A concise sentiment summary is translated into Hindi and converted into audio using Google Cloud TTS. Users can download and play the audio file directly from the application.


### Setup Guide
#### Step 1: Prerequisites
- **Python :** Version 3.9 or higher installed.

- **Docker :** Installed for containerization.

- **Google Cloud Account :** For Text-to-Speech API.

- **Hugging Face Account :** For deploying the app.


#### Step 2: Setting Up Google Cloud for Text-to-Speech

- Create a Google Cloud Project 
Navigate to Google Cloud Console -> Create a new project and enable the Text-to-Speech API.

- Generate Service Account Credentials
    - Go to IAM & Admin → Service Accounts.

    - Create a new service account and assign the Text-to-Speech Admin role.

    - Generate a JSON key file and download it.

- Set Environment Variables
    - Extract **PRIVATE_KEY** and **CLIENT_EMAIL** from the JSON file and store them securely. These will later be set as secrets in Hugging Face Spaces.
    - **CLIENT_EMAIL**: Your gcp client email, can be found in .json file after creating keys in service accounts in google cloud.
    - **PRIVATE_KEY**: Format like- ```"-----BEGIN PRIVATE KEY-----\nMhA==\n-----END PRIVATE KEY-----\n" ``` (Actual key is very long text, this is just for example)

#### Step 3: Preparing Hugging Face Spaces
- Create a New Space
Go to Hugging Face Spaces and select Docker as the runtime environment.

- Add Secrets
    Navigate to the Settings tab in HF space and add the following secrets:

    - **GROQ_API_KEY**: API Key for ChatGroq LLM.

    - **PRIVATE_KEY**: Google TTS private key.

    - **CLIENT_EMAIL**: Service account email.

- Clone the repository created  with space
```bash 
git clone https://huggingface.co/spaces/<user_name>/<space_name>
```
- Expected structure just after cloning repository in Local machine
```bash
<space_name>/
    |__ .gitattributes
    |__ README.md
```

#### Step 4: Open the VSCode or any code editor in this directory (in 'space_name' directory)
- Open terminal in 'space_name' directory.
- Open any code editor in your directory.
- Example of powershell opening VS code from terminal in the cloned repo directory:
```bash
(base) PS D:\Projects\space_name>  code .
```

#### Step 5: Now create the files structure like shown below
```bash
<space_name>/
    |__ .gitattributes
    |__ .gitignore
    |__ backend
    |       |__ api.py
    |       |__ utils.py
    |__ frontend
    |       |__ app.py
    |__ Dockerfile
    |__ README.md
    |__ requirements.txt

```
#### Step 6: Copy the code of the files from this repository.
- Copy the code of these files from this repository to your spaces repository files.


### How files are working

- **1. .gitignore**  
    To mention files or scripts you don't want to push it in your hugging face space.

- **2. utils.py** 

    This file contains the core utility functions that enable the application to extract, analyze, and summarize news data:

    - extract_titles_and_summaries: Scrapes with Economic Times for news articles about the company and extracts their titles and summaries with the help of **BeautifulSoup**.

    - perform_sentiment_analysis: Utilizes Hugging Face's sentiment analysis model ```tabularisai/multilingual-sentiment-analysis``` to classify articles into Positive, Negative, or Neutral.

    - extract_topics_with_hf: Identifies topics from articles using Hugging Face's topic classification model ```valurank/distilroberta-topic-classification```.

    - compare_articles: Compares articles based on sentiment variations and identifies common themes, preparing high-level insights about the company's public perception.

    - generate_final_sentiment: Summarizes the sentiment analysis results and provides an overview of implications for the company's reputation and market performance.

- **2. api.py** 

    - It serves as the backbone for data processing and secure interactions between the backend and frontend.
    - This file builds the backend using FastAPI to serve the application's functionalities:

    - Integrates utils.py: Orchestrates the utility functions to process and analyze news articles.

    - Handles Text-to-Speech: Uses Google Cloud TTS API to generate Hindi audio summaries and Ensures smooth integration of private keys and credentials using environment variables.

    - Defines API Routes:
        - /generateSummary: Creates and serves a detailed sentiment summary.
        - /downloadJson: Serves the JSON summary file for download.
        - /downloadHindiAudio: Serves the Hindi audio file for download.

- **3. app.py**

- This file transforms the processed data into an easy-to-use and visually appealing interface for users.
- This file builds the user interface using Streamlit:
    - Company Input: Users enter the company name to analyze sentiment.
    - Dynamic Visualization: Displays articles, sentiment scores, key topics, and sentiment distribution in an organized format.
    - Download Options: Provides buttons to download the JSON summary and Hindi audio file.
    - Plays Audio: Enables users to play the generated Hindi audio directly within the application.

- **4. Dockerfile**

    - The Dockerfile ensures smooth deployment and execution of the application on Hugging Face Spaces.
    - The Dockerfile containerizes the entire application for deployment:
        - Installs Dependencies: Sets up Python environment and installs all required libraries.
        - Defines Execution Commands: Starts the FastAPI backend on port 8000 and Launches the Streamlit frontend on port 7860.
        - Facilitates Scalability: Ensures compatibility with Hugging Face Spaces and any Docker-enabled platform.

