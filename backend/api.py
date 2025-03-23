# Importing important libraries
from fastapi import FastAPI, Query,HTTPException          
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse          
from google.cloud import texttospeech         
from google.oauth2.service_account import Credentials   
from langchain.schema import HumanMessage   
from langchain_groq import ChatGroq  
import json   
from dotenv import load_dotenv   
import os   

# Importing utility functions for processing news articles
from utils import (  
    extract_titles_and_summaries,
    perform_sentiment_analysis,
    extract_topics_with_hf,
    compare_articles
)

load_dotenv()  # Loading environment variables from .env file
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  
PRIVATE_KEY = os.getenv('PRIVATE_KEY').replace("\\n", "\n")  
CLIENT_EMAIL = os.getenv('CLIENT_EMAIL')  

app = FastAPI(title="Company Sentiment API", description="Get company news summaries with sentiment analysis")  

llm=ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")  

JSON_FILE_PATH = "final_summary.json"  
AUDIO_FILE_PATH = "hindi_summary.mp3"  

def get_tts_client():  # Function to create a Text-to-Speech client
    # Setting up Google Cloud credentials
    credentials = Credentials.from_service_account_info({  
        "type": "service_account",
        "private_key": PRIVATE_KEY,
        "client_email": CLIENT_EMAIL,
        "token_uri": "https://oauth2.googleapis.com/token"
    })
    return texttospeech.TextToSpeechClient(credentials=credentials)  

# Creating main function to create final summarized report 
def generate_summary(company_name):  
    news_articles = extract_titles_and_summaries(company_name)  
    news_articles, sentiment_counts = perform_sentiment_analysis(news_articles)  
    news_articles = extract_topics_with_hf(news_articles) 
    final_summary = compare_articles(news_articles, sentiment_counts)  
    hindi_text = ""  
    if PRIVATE_KEY and CLIENT_EMAIL: 
        hindi_prompt = f"Just Translate this text into Hindi: {final_summary['Final Sentiment Analysis']}"  # Creating a prompt for Hindi translation
        hindi_response = llm.invoke([HumanMessage(content=hindi_prompt)]).content  
        hindi_text = hindi_response.strip() if hindi_response else "Translation not available."  
        if hindi_text: 
            print(f"Generated Hindi Text: {hindi_text}")  
        else:
            print("Hindi Text not generated")  

        try:
            client = get_tts_client()  # Getting the Text-to-Speech client
            input_text = texttospeech.SynthesisInput(text=hindi_text)  # Creating TTS input from Hindi text
            voice = texttospeech.VoiceSelectionParams(  
                language_code="hi-IN",
                name="hi-IN-Chirp3-HD-Kore"
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)  # Configuring MP3 audio output
            response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)  # Synthesizing speech from text
            with open(AUDIO_FILE_PATH, "wb") as out:  # Writing the audio content to a file
                out.write(response.audio_content)
                print(f"Audio content written to file: {AUDIO_FILE_PATH}")  

        except Exception as e:  
            print(f"Error generating audio: {e}")  
        if not os.path.exists(AUDIO_FILE_PATH):  
            print(f"Audio file could not be found at {AUDIO_FILE_PATH}.")  

    final_summary["Audio"] = AUDIO_FILE_PATH  

    with open(JSON_FILE_PATH,"w",encoding="utf-8") as f:  
        json.dump(final_summary,f,ensure_ascii=False, indent=4)  
    
    # Returning a structured summary response
    return {  
        'Company': final_summary["Company"],
        'Articles': [
            {
                'Title': article.get('Title', 'No Title'),  
                'Summary': article.get('Summary', 'No Summary'), 
                'Sentiment': article.get('Sentiment', 'Unknown'),  
                'Score': article.get('Score', 0.0),  
                'Topics': article.get('Topics', [])  
            }
            for article in final_summary["Articles"]  
        ],
        'Comparative Sentiment Score': {  # Structuring sentiment analysis comparison
            'Sentiment Distribution': sentiment_counts,  
            'Coverage Differences': final_summary["Comparative Sentiment Score"].get("Coverage Differences", []),  
            'Topic Overlap': { 
                'Common Topics': final_summary["Comparative Sentiment Score"].get("Topic Overlap", {}).get("Common Topics", []),
                'Unique Topics': final_summary["Comparative Sentiment Score"].get("Topic Overlap", {}).get("Unique Topics", {})
            }
        },
        'Final Sentiment Analysis': final_summary["Final Sentiment Analysis"],  
        'Audio': AUDIO_FILE_PATH  
    }

@app.get("/")  # Defining a GET route for the home endpoint
def home():
    return {"message": "Welcome to the Company Sentiment API"} 

@app.post("/generateSummary")  # Defining a POST route to generate a summary
def get_summary(company_name: str = Query(..., description="Enter company name")):  
    structured_summary = generate_summary(company_name)  
    return structured_summary 

@app.get("/downloadJson")  # Defining a GET route to download the JSON summary
def download_json():
    return FileResponse(JSON_FILE_PATH, media_type="application/json", filename="final_summary.json")  

@app.get("/downloadHindiAudio")  # Defining a GET route to download Hindi audio
def download_audio():
    return FileResponse(AUDIO_FILE_PATH, media_type="audio/mp3", filename="hindi_summary.mp3") 

if __name__ == "__main__":  # Main execution block for running the app
    import uvicorn 
    uvicorn.run(app, host="0.0.0.0", port=8000)  


