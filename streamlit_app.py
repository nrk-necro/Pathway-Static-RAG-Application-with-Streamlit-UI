import streamlit as st
import requests

# Set the base URL for your Pathway RAG API
BASE_URL = "http://localhost:8080"

st.title("Pathway RAG Application with Gemini")

# Sidebar for configuration
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["Ask Question", "Search Documents", "List Documents", "Summarize Texts"])

with tab1:
    st.header("Ask a Question")
    question = st.text_input("Enter your question:")
    use_rag = st.checkbox("Use RAG (Retrieval-Augmented Generation)")
    
    if use_rag:
        filters = st.text_input("Enter filters (optional, e.g., contains(path, `docx`))")
    
    if st.button("Ask"):
        payload = {
            "prompt": question,
        }
        if api_key:
            payload["gemini_api_key"] = api_key
        if use_rag and filters:
            payload["filters"] = filters
        
        response = requests.post(f"{BASE_URL}/v1/pw_ai_answer", json=payload)
        if response.status_code == 200:
            st.subheader("Answer:")
            st.write(response.text)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

with tab2:
    st.header("Search Documents")
    search_query = st.text_input("Enter search query:")
    k = st.number_input("Number of results (k)", min_value=1, value=5)
    
    if st.button("Search"):
        payload = {
            "query": search_query,
            "k": k
        }
        response = requests.post(f"{BASE_URL}/v1/retrieve", json=payload)
        if response.status_code == 200:
            try:
                results = response.json()
                for idx, result in enumerate(results, 1):
                    st.subheader(f"Result {idx}")
                    st.write(f"Score: {result['score']}")
                    st.write(f"Content: {result['content']}")
                    st.write(f"Metadata: {result['metadata']}")
            except requests.exceptions.JSONDecodeError:
                st.warning("Response is not in JSON format. Raw response:")
                st.text(response.text)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

with tab3:
    st.header("List Documents")
    if st.button("Fetch Documents"):
        response = requests.post(f"{BASE_URL}/v1/pw_list_documents")
        if response.status_code == 200:
            try:
                documents = response.json()
                for doc in documents:
                    st.subheader(doc["path"])
                    st.write(f"Size: {doc['size']} bytes")
                    st.write(f"Last Modified: {doc['last_modified']}")
            except requests.exceptions.JSONDecodeError:
                st.warning("Response is not in JSON format. Raw response:")
                st.text(response.text)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

with tab4:
    st.header("Summarize Texts")
    texts = st.text_area("Enter texts to summarize (one per line):")
    
    if st.button("Summarize"):
        text_list = texts.split('\n')
        payload = {
            "text_list": text_list,
        }
        if api_key:
            payload["gemini_api_key"] = api_key
        response = requests.post(f"{BASE_URL}/v1/pw_ai_summary", json=payload)
        if response.status_code == 200:
            st.subheader("Summary:")
            st.write(response.text)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")

# Display statistics
st.sidebar.header("Statistics")
if st.sidebar.button("Fetch Statistics"):
    response = requests.post(f"{BASE_URL}/v1/statistics")
    if response.status_code == 200:
        try:
            stats = response.json()
            st.sidebar.write(f"Number of documents: {stats['num_documents']}")
            st.sidebar.write(f"Number of chunks: {stats['num_chunks']}")
        except requests.exceptions.JSONDecodeError:
            st.sidebar.warning("Statistics response is not in JSON format. Raw response:")
            st.sidebar.text(response.text)
    else:
        st.sidebar.error(f"Error fetching statistics: {response.status_code} - {response.text}")
