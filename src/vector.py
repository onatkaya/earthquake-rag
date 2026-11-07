"""
Vector Database Setup for EarthquakeRAG

This module initializes and manages the vector database (Chroma) that stores embeddings
of all earthquake-related tweets. It handles:

1. **Data Loading**: Reads the pre-processed tweet dataset from CSV
2. **Embedding Generation**: Converts tweets to dense vector embeddings using mxbai-embed-large
3. **Database Creation**: Sets up a local Chroma vector store for semantic search
4. **Retriever Setup**: Creates a semantic search retriever for finding relevant tweets

The retriever is used by main.py to find the most relevant tweets for answering user questions
through semantic similarity search, rather than keyword matching.

Key components:
- embeddings: OllamaEmbeddings model for converting text to vectors
- vector_store: Chroma database storing tweet embeddings
- retriever: Interface for semantic search against the database (returns top-k most relevant tweets)

The vector database is persisted locally, so it's built only once on first run,
then reused on subsequent runs for faster startup.
"""
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

# ===== DATA LOADING =====
# Project root - computed from this file's location for path independence
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the pre-processed tweet dataset (no index column in CSV)
df = pd.read_csv(os.path.join(project_root, "data", "dataset.csv"))

# ===== EMBEDDING MODEL =====
# Initialize the embedding model for converting tweets to dense vectors
# mxbai-embed-large: Multilingual model optimized for semantic search
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# ===== VECTOR DATABASE =====
# Path where the local Chroma vector database is persisted
db_location = os.path.join(project_root, "chrome_langchain_db")

# Check if database needs to be built (first run) or reused (subsequent runs)
# This optimization avoids expensive re-embedding of all tweets
add_documents = not os.path.exists(db_location)

# On first run: Convert tweets to documents and embed them
if add_documents:
    documents = []
    ids = []

    # Convert each CSV row to a Document with the tweet text and class label
    # Format: "<class> <tweet_text>" e.g., "Yardım Çağrısı Kahramanmaraş'ta yardım lazım..."
    for i, row in df.iterrows():
        document = Document(
            page_content=row["Class"] + " " + row["Tweets"],
            id=str(i)
        )
        ids.append(str(i))
        documents.append(document)

# Initialize or load the Chroma vector database
vector_store = Chroma(
    collection_name="deprem_tweet",
    persist_directory=db_location,
    embedding_function=embeddings
)

# On first run: Add all documents to the vector store and embed them
if add_documents:
    print("Building vector database... (this may take a moment on first run)")
    vector_store.add_documents(documents=documents, ids=ids)
    print(f"Database built successfully with {len(documents)} tweets")

# ===== SEMANTIC SEARCH RETRIEVER =====
# Create a retriever that performs semantic similarity search
# When main.py asks a question, this retriever finds the k most relevant tweets
retriever = vector_store.as_retriever(
    search_kwargs={"k": 30}  # Return top k-most relevant tweets for each query
)

