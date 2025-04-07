# secure-rag/app/indexing.py

import json
import os
from langchain_community.vectorstores import FAISS

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from dotenv import load_dotenv
import logging
load_dotenv() # Load environment variables from .env file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_PATH = "../data/docs.json" # Path relative to this script
VECTORSTORE_PATH = "../vectorstore" # Directory to save the FAISS index
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Use a standard Google embedding model compatible with the Gemini API
GOOGLE_EMBEDDING_MODEL = "models/embedding-001"

def load_docs_from_json(file_path: str) -> list[Document]:
    """Loads documents from a JSON file and creates LangChain Document objects."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.info(f"Error: The file {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        logger.info(f"Error: Could not decode JSON from the file {file_path}.")
        return []

    langchain_docs = []
    for item in data:
        if not all(k in item for k in ["title", "content", "permission"]):
            logger.info(f"Warning: Skipping item due to missing fields: {item.get('title', 'N/A')}")
            continue
            
        metadata = {
            "title": item.get("title", "Unknown Title"),
            "category": item.get("category", "Uncategorized"),
            "permission": item["permission"] 
        }
        
        doc = Document(page_content=item["content"], metadata=metadata)
        langchain_docs.append(doc)
        
    logger.info(f"Loaded {len(langchain_docs)} documents from {file_path}")
    return langchain_docs

def create_and_save_vectorstore(docs: list[Document], save_path: str):
    """Creates and saves a FAISS vector store from documents using Google Embeddings."""
    if not docs:
        logger.info("No documents loaded, skipping vector store creation.")
        return

    logger.info(f"Processing {len(docs)} documents for vectorization...")
    
    # 1. Split Documents into Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    logger.info(f"Split documents into {len(chunks)} chunks.")

    # 2. Initialize Embedding Model (Using Google)
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=GOOGLE_EMBEDDING_MODEL)
    except Exception as e:
        logger.info(f"Error initializing Google Embeddings. Ensure GOOGLE_API_KEY is set correctly. Error: {e}")
        return

    # 3. Create FAISS Vector Store
    logger.info("Creating FAISS vector store... This might take a moment.")
    try:
        vectorstore = FAISS.from_documents(chunks, embeddings)
    except Exception as e:
         logger.info(f"Error creating FAISS index: {e}")
         return

    # 4. Save Vector Store Locally
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    vectorstore.save_local(save_path)
    logger.info(f"FAISS vector store created and saved successfully at {save_path}")

# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Starting SecureRAG indexing process using Google Embeddings...")
    
    documents = load_docs_from_json(DATA_PATH)
    
    create_and_save_vectorstore(documents, VECTORSTORE_PATH)
    
    logger.info("Indexing process finished.")