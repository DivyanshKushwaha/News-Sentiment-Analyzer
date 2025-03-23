# Importing libraries
from bs4 import BeautifulSoup
import requests
from langchain.schema import HumanMessage
from langchain_groq import ChatGroq
import json
from dotenv import load_dotenv
import os
from transformers import pipeline

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Initialize the LLM model
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant")

# Function to extract news titles and summaries from Economic Times
def extract_titles_and_summaries(company_name, num_articles=10):
    url = f"https://economictimes.indiatimes.com/topic/{company_name}/news"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch the webpage. Status code: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all('div', class_='clr flt topicstry story_list', limit=num_articles)
        extracted_articles = []

        for article in articles:
            title_tag = article.find('h2')
            if title_tag:
                link_tag = title_tag.find('a')
                title = link_tag.get_text(strip=True) if link_tag else "No Title Found"
            else:
                title = "No Title Found"

            summary_tag = article.find('p')
            summary = summary_tag.get_text(strip=True) if summary_tag else "No Summary Found"

            extracted_articles.append({
                "Title": title,
                "Summary": summary
            })

        return {
            "Company": company_name,
            "Articles": extracted_articles
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Function to perform sentiment analysis on extracted news articles
def perform_sentiment_analysis(news_data):
    from transformers import pipeline
    articles = news_data.get("Articles", [])
    pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=1)
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for article in articles:
        content = f"{article['Title']} {article['Summary']}"
        sentiment_result = pipe(content)[0]

        sentiment_map = {
            "positive": "Positive",
            "negative": "Negative",
            "neutral": "Neutral",
            "very positive": "Positive",
            "very negative": "Negative"
        }

        sentiment = sentiment_map.get(sentiment_result["label"].lower(), "Unknown")
        score = float(sentiment_result["score"])

        article["Sentiment"] = sentiment
        article["Score"] = score

        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

    return news_data, sentiment_counts

# Function to extract topics from articles using Hugging Face model
def extract_topics_with_hf(news_data):
    structured_data = {
        "Company": news_data.get("Company", "Unknown"),
        "Articles": []
    }
    topic_pipe = pipeline("text-classification", model="valurank/distilroberta-topic-classification", device=1)
    articles = news_data.get("Articles", [])

    for article in articles:
        content = f"{article['Title']} {article['Summary']}"
        topics_result = topic_pipe(content, top_k=3)
        topics = [topic["label"] for topic in topics_result] if topics_result else ["Unknown"]

        structured_data["Articles"].append({
            "Title": article["Title"],
            "Summary": article["Summary"],
            "Sentiment": article.get("Sentiment", "Unknown"),
            "Score": article.get("Score", 0.0),
            "Topics": topics
        })
    return structured_data

# Function to generate a final sentiment summary using LLM
def generate_final_sentiment(news_data, sentiment_counts):
    company_name = news_data["Company"]
    total_articles = sum(sentiment_counts.values())
    combined_summaries = " ".join([article["Summary"] for article in news_data["Articles"]])

    prompt = f"""
    Based on the analysis of {total_articles} articles about the company "{company_name}":
    - Positive articles: {sentiment_counts['Positive']}
    - Negative articles: {sentiment_counts['Negative']}
    - Neutral articles: {sentiment_counts['Neutral']}
    The following are the summarized key points from the articles: "{combined_summaries}".
    Provide a single, concise summary that integrates the overall sentiment analysis and key news highlights while maintaining a natural flow. Explain its implications for the company's reputation, stock potential, and public perception.
    Respond **ONLY** with a well-structured very concise and short paragraph in plain text, focusing on overall sentiment.
    """

    response = llm.invoke([HumanMessage(content=prompt)], max_tokens=200)
    final_sentiment = response if response else "Sentiment analysis summary not available."
    return final_sentiment.content  # returns a string

# Function to extract JSON response from LLM output
def extract_json(response):
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {}

# Function to compare articles based on common topics and sentiment variations
def compare_articles(news_data, sentiment_counts):
    articles = news_data.get("Articles", [])
    all_topics = [set(article["Topics"]) for article in articles]
    common_topics = set.intersection(*all_topics) if all_topics else set()

    topics_prompt = f"""
    Analyze the following article topics and identify **only three** key themes that are common across multiple articles, 
    even if they are phrased differently. The topics from each article are:
    {all_topics}

    Respond **ONLY** with a JSON format:
    {{"CommonTopics": ["topic1", "topic2", "topic3"]}}
    """
    
    response = llm.invoke([HumanMessage(content=topics_prompt)]).content
    contextual_common_topics = extract_json(response).get("CommonTopics", list(common_topics))[:3]  # Limit to 3 topics

    total_articles = sum(sentiment_counts.values())

    comparison_prompt = f"""
    Provide a high-level summary comparing {total_articles} news articles about "{news_data['Company']}":
    - Sentiment distribution: {sentiment_counts}
    - Commonly discussed topics across articles: {contextual_common_topics}

    Consider the following:
    1. Notable contrasts between articles (e.g., major differences in topics and perspectives).
    2. Overall implications for the company's reputation, stock potential, and public perception.
    3. How sentiment varies across articles and its impact.

    Respond **ONLY** with a concise and insightful summary in this JSON format:
    {{
        "Coverage Differences": [
            {{"Comparison": "Brief contrast between Articles 1 & 2", "Impact": "Concise impact statement"}},
            {{"Comparison": "Brief contrast between Articles 3 & 4", "Impact": "Concise impact statement"}}
        ]
    }}
    """

    response = llm.invoke([HumanMessage(content=comparison_prompt)]).content
    coverage_differences = extract_json(response).get("Coverage Differences", [])

    final_sentiment = generate_final_sentiment(news_data, sentiment_counts)

    return {
        "Company": news_data["Company"],
        "Articles": articles,
        "Comparative Sentiment Score": {
            "Sentiment Distribution": sentiment_counts,
            "Coverage Differences": coverage_differences,  
            "Topic Overlap": {
                "Common Topics": contextual_common_topics,
                "Unique Topics": {
                    f"Article {i+1}": list(topics - set(contextual_common_topics))
                    for i, topics in enumerate(all_topics)
                }
            }
        },
        "Final Sentiment Analysis": final_sentiment
    }
