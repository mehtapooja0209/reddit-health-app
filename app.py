import streamlit as st
import pandas as pd
import plotly.express as px
import json
import gdown
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reddit Health Insights", layout="wide")

@st.cache_data
def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@st.cache_data
def json_to_df(data):
    return pd.json_normalize(data)

# App title
st.title("💊 Reddit Health Data Explorer")

# Option to download from Google Drive
drive_url = st.text_input("https://drive.google.com/file/d/1gNcVIQMJMRvbm8d5yR2DsmVdh1vBAnCq/view?usp=drive_link")
if drive_url and st.button("Download & Load JSON from Drive"):
    file_id = drive_url.split("/")[-2]
    output = "reddit_data.json"
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)
    data = load_json_data(output)
    df = json_to_df(data)

# Or upload local JSON file
uploaded = st.file_uploader("📁 Or Upload Your Processed JSON File", type="json")
if uploaded:
    data = json.load(uploaded)
    df = json_to_df(data)

if 'df' in locals():
    st.success("Data Loaded!")

    # Filters
    st.sidebar.header("🔍 Filters")
    categories = st.sidebar.multiselect("Filter by Category", df['categories'].explode().dropna().unique())
    sentiments = st.sidebar.multiselect("Sentiment", df['sentiment.label'].unique())

    filtered_df = df.copy()
    if categories:
        filtered_df = filtered_df[filtered_df['categories'].apply(lambda x: any(cat in x for cat in categories))]
    if sentiments:
        filtered_df = filtered_df[filtered_df['sentiment.label'].isin(sentiments)]

    st.subheader("📊 Sentiment Over Time")
    if 'metadata.created_utc' in df.columns:
        filtered_df['created_utc'] = pd.to_datetime(filtered_df['metadata.created_utc'], errors='coerce')
        time_data = filtered_df.groupby(filtered_df['created_utc'].dt.to_period("M"))['sentiment.score'].mean().reset_index()
        time_data['created_utc'] = time_data['created_utc'].astype(str)
        fig = px.line(time_data, x='created_utc', y='sentiment.score', title="Average Sentiment Over Time")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("💬 Top Symptoms Mentioned")
    all_entities = sum(filtered_df['entities'].dropna(), [])
    symptoms_df = pd.DataFrame([ent for ent in all_entities if ent['type'] == 'DISEASE'])
    top_symptoms = symptoms_df['text'].value_counts().head(20)
    st.bar_chart(top_symptoms)

    st.subheader("☁️ Word Cloud of Symptoms")
    text = ' '.join(symptoms_df['text'].tolist())
    wc = WordCloud(width=1000, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    st.subheader("📥 Download Filtered Data")
    st.download_button("Download JSON", json.dumps(filtered_df.to_dict(orient='records'), indent=2), file_name="filtered_reddit_data.json", mime="application/json")
