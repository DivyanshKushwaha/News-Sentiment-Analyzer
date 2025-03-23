## News Sentiment Analyzer
This repository contains an application that extracts news articles for a specific company, analyzes their sentiment, identifies key topics, and provides insightful summaries. Additionally, it generates audio summaries in Hindi using Google Cloud Text-to-Speech (TTS). The application is deployed on Hugging Face Spaces for easy access and scalability.

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


### Project Structure

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
### How files are working

- **1. .gitignore**  
    To mention files or scripts you don't want to push it in your hugging face space.

- **2. utils.py (LLM Models Implementation)** 

    This file contains the core utility functions that enable the application to extract, analyze, and summarize news data:

    - extract_titles_and_summaries: 
        - Scrapes news about the company from Economic Times website.
        - Extracts their titles and summaries with the help of **BeautifulSoup**.

    - perform_sentiment_analysis:
        - Utilizes Hugging Face's sentiment analysis model ```tabularisai/multilingual-sentiment-analysis```
        - Classifies articles into Positive, Negative, or Neutral.
        - Code example:
            ```bash
            from transformers import pipeline
            pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=1)
            sentiment_result = pipe(content)[0]
            ```

    - extract_topics_with_hf: 
        - Uses Hugging Face's topic classification model ```valurank/distilroberta-topic-classification```
        - Identifies topics from articles.
        - Code example:
            ```bash
            topic_pipe = pipeline("text-classification", model="valurank/distilroberta-topic-classification", device=1)
            topics_result = topic_pipe(content, top_k=3)
            ```

    - compare_articles:
        - Compares articles based on sentiment variations and identifies common themes, 
        - Prepare high-level insights about the company's public perception.

    - generate_final_sentiment: 
        - Summarizes the sentiment analysis results.
        - Uses LLM model ```llama-3.1-8b-instant``` from **GroqAI**
        - Code example:
            ```bash 
                llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")
                response = llm.invoke([HumanMessage(content=prompt)], max_tokens=200)
            ```

- **2. api.py (API Development)** 

    - It serves as the backbone for interactions between the backend and frontend, builds the backend using FastAPI.
    - Orchestrates the utility functions to process and analyze news articles.
    - API Endpoints:
        - Home (GET /) : Welcome Endpoint
            ```bash
            {"message": "Welcome to the Company Sentiment API"}
            ```

        - Generate Summary (POST /generateSummary): Processes articles, performs sentiment analysis, and generates summaries.

            ```bash
            Parameters: company_name (Query): Name of the company to analyze.
            Usage (POST via Postman): http://127.0.0.1:8000/generateSummary?company_name=Microsoft
            Response:
                {
                "Company": "Microsoft",
                "Articles": [...],
                "Comparative Sentiment Score": {...},
                "Final Sentiment Analysis": "Positive sentiment overall...",
                "Audio": "hindi_summary.mp3"
                }

            ```

        - Download JSON (GET /downloadJson): Downloads the JSON summary.
            ```bash
            Usage: Access http://127.0.0.1:8000/downloadJson.
            ```

        - Download Hindi Audio (GET /downloadHindiAudio): Downloads the Hindi audio summary.

            ```bash
            Usage: Access http://127.0.0.1:8000/downloadHindiAudio.
            Handles Text-to-Speech: Uses Google Cloud TTS API to generate Hindi audio summaries.

                client = texttospeech.TextToSpeechClient(credentials=credentials)
                input_text = texttospeech.SynthesisInput(text=hindi_text)
                response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)


            ```

- **3. app.py (UI Development)**

    - This file builds the user interface using Streamlit:
        - Dynamic Visualization: Displays articles, sentiment scores, key topics, and sentiment distribution in an organized format.
        - Download Options: Provides buttons to download the JSON summary and Hindi audio file.
        - Plays Audio: Enables users to play the generated Hindi audio directly within the application.

- **4. Dockerfile**

    - The Dockerfile containerizes the entire application for deployment:
        - Installs Dependencies: Sets up Python environment and installs all required libraries.
        - Defines Execution Commands: Starts the FastAPI backend on port 8000 and Launches the Streamlit frontend on port 7860.


### Usage and Installation

- #### To run Locally

    - Clone the Repository
        ```bash
        git clone https://github.com/your-repo/news-sentiment-analyzer.git
        cd news-sentiment-analyzer
        ```
    - Install Python Dependencies
        ```
        bash
        pip install -r requirements.txt
        ```
    - Set Up Google Cloud TTS Credentials and all APIs as mentioned in above (In setup Guide)

    - Start the Backend (FastAPI)
        ```bash
        python backend/api.py
        ```

    - Start the Frontend (Streamlit)
        - First change the BASE_URL in app.py, put this BASE_URL : ```BASE_URL = http://127.0.0.1:8000```
        - Then run the frontend app
            ```bash
            streamlit run app.py
            ```

- #### To Run the App on Hugging Face Spaces

    - Setup the Hugging Face Space (Read Setup Guide)

    - Upload the following project files to the created Space:

        - utils.py
        - api.py
        - app.py
        - Dockerfile
        - requirements.txt

    - Hugging Face will automatically deploy the application using the Dockerfile

    - Test the Application by accessing Space’s URL provided by Hugging Face.

### Third-Party API Usage
- Hugging Face Models: Download pre-trained models from Hugging Face using transformers library.

- Google Cloud Text-to-Speech: Generate hindi audio summaries.

- GroqAI LLM Model: To summarize the sentiments of articles.

