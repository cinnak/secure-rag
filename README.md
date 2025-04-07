# SecureRAG: Permission-Aware RAG System

## Overview

SecureRAG is a Retrieval-Augmented Generation (RAG) system built with Python and LangChain. Its core feature is enforcing data access control based on user roles (e.g., Engineer, HR, Product Manager). The system ensures that users can only ask questions and receive answers based on the documents they have permission to access. It leverages Google AI (Gemini) for embeddings and language generation, and FAISS for efficient vector storage and retrieval.

## Features

* **Role-Based Access Control:** Filters retrieved documents based on user roles defined in document metadata.
* **RAG Pipeline:** Implements a standard RAG pipeline: Load -> Split -> Embed -> Store -> Retrieve -> Generate.
* **Modular Design:** Uses distinct components for indexing, retrieval, and the main RAG chain.
* **Google Gemini Integration:** Utilizes Google's models for text embedding and chat generation.
* **Simple UI:** Includes a basic Streamlit interface for interaction.

## Tech Stack

* Python 3.x
* LangChain (`langchain`, `langchain-google-genai`, `langchain-community`)
* Google Generative AI (`google-generativeai`)
* FAISS (`faiss-cpu`)
* Streamlit (for UI)
* `python-dotenv` (for API key management)

## Project Structure

```
secure-rag/
├── .env                  # Local environment variables (API Key - NOT COMMITTED)
├── .env.example          # Example environment file
├── .gitignore            # Specifies intentionally untracked files
├── README.md             # This file
├── requirements.txt      # Python dependencies
├── data/
│   └── docs.json         # Sample documents with permission metadata
├── app/
│   ├── __init__.py
│   ├── indexing.py       # Script to create the vector store index
│   ├── retriever.py      # Defines the PermissionRetriever class
│   └── rag_chain.py      # Defines the core RAG chain logic
├── tests/
│   ├── __init__.py
│   ├── test_retriever.py # Script to test the retriever
│   └── test_rag_chain.py # Script to test the RAG chain
├── ui/
│   └── interface.py      # Streamlit user interface script
└── vectorstore/          # Directory storing the FAISS index (NOT COMMITTED)

```

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url> # Replace with your repo URL if applicable
    cd secure-rag
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Activate the environment (adjust for your OS)
    # Linux/macOS:
    source .venv/bin/activate
    # Windows (Git Bash):
    # source .venv/Scripts/activate
    # Windows (CMD):
    # .\.venv\Scripts\activate.bat
    # Windows (PowerShell):
    # .\.venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    * Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    * Edit the `.env` file and add your Google API Key:
        ```dotenv
        GOOGLE_API_KEY=YOUR_ACTUAL_GOOGLE_API_KEY
        ```

## Running the Application

1.  **Create the Vector Store (First time only):**
    * Ensure your `.env` file is set up.
    * Run the indexing script from the project root directory:
        ```bash
        python app/indexing.py
        ```
    * This will create the `vectorstore/` directory containing the FAISS index.

2.  **Run Tests (Optional):**
    * Run retriever tests:
        ```bash
        python tests/test_retriever.py --role Engineer --query "deployment"
        ```
    * Run RAG chain tests:
        ```bash
        python tests/test_rag_chain.py
        ```

3.  **Run the User Interface:**
    * Start the Streamlit application from the project root directory:
        ```bash
        streamlit run ui/interface.py
        ```
    * Open the URL provided by Streamlit (usually `http://localhost:8501`) in your browser.
    * Select a role, enter a query, and click "Submit".

## How it Works

1.  **Indexing:** Documents from `data/docs.json` are loaded, chunked, and embedded using a Google embedding model. The resulting vectors and their associated metadata (including `permission` lists) are stored in a FAISS index.
2.  **UI Interaction:** The user selects a role and enters a query via the Streamlit UI.
3.  **RAG Chain Invocation:** The UI calls the `get_rag_response` function in `app/rag_chain.py`, passing the query and selected role.
4.  **Permissioned Retrieval:** The `PermissionRetriever` performs a similarity search in the FAISS index for the query. It then filters the retrieved document chunks, keeping only those whose `permission` metadata includes the user's role.
5.  **Contextual Generation:** The permission-filtered document chunks are formatted into a context string. This context, along with the original query, is passed to a Google chat model (e.g., `gemini-1.0-pro`) via a prompt template.
6.  **Response:** The LLM generates an answer based *only* on the provided, permission-filtered context. This answer is returned to the UI and displayed to the user.

## Future Enhancements

* Implement user authentication instead of role simulation.
* Add conversation history/memory.
* Explore finer-grained access control (e.g., section-level permissions).
* Improve UI/UX (e.g., streaming responses, displaying sources).
* Add comprehensive automated testing (unit, integration).
* Implement audit logging for queries and access.
