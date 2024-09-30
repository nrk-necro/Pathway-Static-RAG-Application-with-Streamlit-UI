import streamlit as st
import requests

# Set the base URL for your Pathway RAG API
BASE_URL = "http://localhost:8000"

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="Pathway RAG with Gemini", page_icon="Pa")

# Custom CSS for improved design
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    /* Styling the scroll bar */
    ::-webkit-scrollbar {
        width: 16px; /* Make it thicker */
    }
    ::-webkit-scrollbar-track {
        background: #1e2530;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #4CAF50; /* You can change this to your preferred color */
        border-radius: 10px;
        border: 3px solid #1e2530; /* To create space between scrollbar and edge */
    }
    
    /* Firefox scrollbar styles */
    body {
        scrollbar-width: thin;
        scrollbar-color: white #1e2530;
    }

    /* Ensure scroll bar is always visible */
    .stApp {
        overflow-y: scroll;
    }

    /* Adjust margins to push scrollbar to the edge */
    .stApp {
        padding-right: 40px; /* Adjust the padding to move the scrollbar closer to the edge */
    }

    .stTextInput > div > div > input {
        background-color: #2b313e;
    }
    .stTextArea > div > div > textarea {
        background-color: #2b313e;
    }
    .stButton > button {
        width: 100%;
    }
    .css-1y4p8pa {
        padding-top: 2rem;
    }
    .css-1544g2n {
        padding-top: 2rem;
    }
    .stMarkdown {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1e2530;
    }
</style>
""", unsafe_allow_html=True)

# App title with custom styling
st.markdown("<h1 style='text-align: center; color: white;'>Pathway RAG Application with Gemini</h1>", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Gemini API Key", type="password")
    
    # Add some space
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fetch statistics button
    if st.button("Fetch Statistics", key="fetch_stats"):
        response = requests.post(f"{BASE_URL}/v1/statistics")
        if response.status_code == 200:
            stats = response.json()
            st.success("Statistics fetched successfully!")
            st.metric("Number of documents", stats['num_documents'])
            st.metric("Number of chunks", stats['num_chunks'])
        else:
            st.error(f"Error fetching statistics: {response.status_code}")

# Main content area
tab1, tab2, tab3 = st.tabs(["Ask Question", "List Documents", "Summarize Texts"])

with tab1:
    st.header("Ask a Question")
    
    # Create a card-like container for the question input
    question_container = st.container()
    with question_container:
        
        question = st.text_area("", height=100, key="question_input")
        col1, col2 = st.columns([3, 1])
        with col1:
            use_rag = st.checkbox("Use RAG (Retrieval-Augmented Generation)")
        with col2:
            ask_button = st.button("Ask", key="ask_button", use_container_width=True)
    
    if use_rag:
        filters = st.text_input("Enter filters (optional, e.g., contains(path, `docx`))")
    
    if ask_button:
        if not question:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Processing your question..."):
                payload = {
                    "prompt": question,
                }
                if api_key:
                    payload["gemini_api_key"] = api_key
                if use_rag and filters:
                    payload["filters"] = filters
                
                response = requests.post(f"{BASE_URL}/v1/pw_ai_answer", json=payload)
                if response.status_code == 200:
                    st.success("Answer received!")
                    st.markdown("### Answer:")
                    st.markdown(response.text)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

with tab2:
    st.header("List Documents")
    if st.button("Fetch Documents", key="fetch_docs"):
        with st.spinner("Fetching documents..."):
            response = requests.post(f"{BASE_URL}/v1/pw_list_documents")
            if response.status_code == 200:
                try:
                    documents = response.json()
                    for doc in documents:
                        with st.expander(doc.get("path", "Unnamed Document")):
                            for key, value in doc.items():
                                if key != "path":
                                    st.markdown(f"**{key.capitalize()}:** {value}")
                except requests.exceptions.JSONDecodeError:
                    st.warning("Response is not in JSON format. Raw response:")
                    st.code(response.text)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

with tab3:
    st.header("Summarize Texts")
    texts = st.text_area("Enter texts to summarize (one per line):", height=200)
    
    if st.button("Summarize", key="summarize_button"):
        if not texts:
            st.warning("Please enter some text to summarize.")
        else:
            with st.spinner("Summarizing texts..."):
                text_list = texts.split('\n')
                payload = {
                    "text_list": text_list,
                }
                if api_key:
                    payload["gemini_api_key"] = api_key
                response = requests.post(f"{BASE_URL}/v1/pw_ai_summary", json=payload)
                if response.status_code == 200:
                    st.success("Summary generated!")
                    st.markdown("### Summary:")
                    st.markdown(response.text)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
