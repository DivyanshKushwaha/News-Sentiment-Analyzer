import streamlit as st
import requests

BASE_URL = "http://localhost:8000"  # Base URL for API requests
st.title("Company Sentiment Analysis")

# Input field for company name
company_name = st.text_input(
    "Enter the company name:",
    placeholder="Example: Microsoft, Apple, Tesla"
)

# Function to display articles with sentiment analysis
def display_articles(articles):
    for i, article in enumerate(articles, start=1):
        st.markdown(f"##### **Article {i}: {article['Title']}**")
        st.write(f"- **Summary:** {article['Summary']}")
        st.write(f"- **Sentiment:** {article['Sentiment']} | **Score:** {article['Score']:.2f}")
        st.write(f"- **Topics:** {', '.join(article['Topics'])}")

# Function to display sentiment distribution in table format
def display_sentiment_distribution(sentiment_distribution):
    st.markdown("#### **Sentiment Distribution:**")
    sentiment_data = {
        "Sentiment": list(sentiment_distribution.keys()),
        "Count": list(sentiment_distribution.values())
    }
    st.table(sentiment_data)

# Function to display coverage differences between articles
def display_coverage_differences(coverage_differences):
    if coverage_differences:
        st.markdown("#### **Coverage Differences:**")
        for diff in coverage_differences:
            st.write(f"- **{diff['Comparison']}:** {diff['Impact']}")

# Function to display topic overlap analysis
def display_topic_overlap(topic_overlap):
    st.markdown("#### **Topic Overlap:**")
    st.write(f"- **Common Topics:** {', '.join(topic_overlap['Common Topics'])}")
    st.markdown("- **Unique Topics by Article:**")
    for article, topics in topic_overlap["Unique Topics"].items():
        st.write(f"  - **{article}:** {', '.join(topics)}")

# Button to generate summary based on company name
if st.button("Generate Summary"):
    if company_name:
        try:
            summary_url = f"{BASE_URL}/generateSummary?company_name={company_name}"
            response = requests.post(summary_url)

            if response.status_code == 200:
                data = response.json()
                st.markdown(f"#### **Company: {data.get('Company', 'Unknown')}**")
                
                # Display articles with sentiment analysis
                st.markdown("#### **Articles:**")
                display_articles(data.get("Articles", []))
                
                # Display sentiment analysis details
                st.markdown("#### **Comparative Sentiment Score:**")
                sentiment_distribution = data.get("Comparative Sentiment Score", {}).get("Sentiment Distribution", {})
                display_sentiment_distribution(sentiment_distribution)
                
                coverage_differences = data.get("Comparative Sentiment Score", {}).get("Coverage Differences", [])
                display_coverage_differences(coverage_differences)
                
                topic_overlap = data.get("Comparative Sentiment Score", {}).get("Topic Overlap", {})
                display_topic_overlap(topic_overlap)
                
                # Display final sentiment analysis result
                st.markdown("#### **Final Sentiment Analysis:**")
                st.write(data.get("Final Sentiment Analysis", "No sentiment analysis available."))
                
                # Display and play Hindi summary audio
                st.markdown("#### **Hindi Summary Audio:**")
                st.write(data.get("Audio", "No Audio available"))
                audio_url = f"{BASE_URL}/downloadHindiAudio"
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    st.audio(audio_response.content, format="audio/mp3")
                else:
                    st.error("Failed to load audio.")
            else:
                st.error(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a company name !")

# Button to download the final summary in JSON format
if st.button("Download JSON File"):
    json_url = f"{BASE_URL}/downloadJson"
    try:
        response = requests.get(json_url)
        if response.status_code == 200:
            st.download_button(
                label="Download JSON File",
                data=response.content,
                file_name="final_summary.json",
                mime="application/json",
            )
        else:
            st.error(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Button to download Hindi summary audio file
if st.button("Download Hindi Audio"):
    audio_url = f"{BASE_URL}/downloadHindiAudio"
    try:
        response = requests.get(audio_url)
        if response.status_code == 200:
            st.download_button(
                label="Download Hindi Audio",
                data=response.content,
                file_name="hindi_summary.mp3",
                mime="audio/mp3",
            )
        else:
            st.error(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
