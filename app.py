import streamlit as st
import gdown
import json

# Download data from Google Drive
@st.cache_data
def load_data():
    file_id = "1gNcVIQMJMRvbm8d5yR2DsmVdh1vBAnCq" # Replace with your ID
    url = f"https://drive.google.com/uc?id={1gNcVIQMJMRvbm8d5yR2DsmVdh1vBAnCq}"
    output = "endo_data.json"
    gdown.download(url, output, quiet=True)
    
    with open(output, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# App UI
st.title("Endometriosis Insights Hub 🩺")
st.write("Search experiences from Reddit posts about endometriosis.")

# Search & Filters
search_term = st.text_input("Search posts...")
selected_category = st.selectbox(
    "Filter by category", 
    ["All"] + sorted({cat for post in data for cat in post['categories']})
)
selected_sentiment = st.selectbox(
    "Filter by sentiment", 
    ["All"] + sorted({post['sentiment']['label'] for post in data})
)
selected_subreddit = st.selectbox(
    "Filter by subreddit", 
    ["All"] + sorted({post['metadata']['subreddit'] for post in data})
)

# Apply filters
filtered_data = data
if search_term:
    filtered_data = [
        post for post in filtered_data 
        if search_term.lower() in post["text"].lower()
    ]
if selected_category != "All":
    filtered_data = [
        post for post in filtered_data 
        if selected_category in post["categories"]
    ]
if selected_sentiment != "All":
    filtered_data = [
        post for post in filtered_data 
        if post["sentiment"]["label"] == selected_sentiment
    ]
if selected_subreddit != "All":
    filtered_data = [
        post for post in filtered_data 
        if post["metadata"]["subreddit"] == selected_subreddit
    ]

# Display results
st.subheader(f"Found {len(filtered_data)} posts")
for post in filtered_data[:100]:  # Show first 100 for performance
    with st.expander(f"Post {post['id']} | Sentiment: {post['sentiment']['label']}"):
        st.write(f"**Posted in**: {post['metadata']['subreddit']}")
        st.write(f"**Date**: {post['metadata']['created_utc']}")
        st.write(f"**Categories**: {', '.join(post['categories'])}")
        st.write("**Key Entities**:")
        for ent in post["entities"]:
            st.write(f"- `{ent['type']}: {ent['text']}`")
        st.write(f"**Topics**: {post['topics']['label']}")
        st.write("**Excerpt**: " + " [...] ".join(post["sentences"][:3]))
