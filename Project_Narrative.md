### SecureRAG Project STAR Framework Narrative

**Situation:**

In a typical company (like the simulated "AI Tech Solutions Inc."), there exists a large volume of knowledge documents, such as technical specifications, HR policies, product roadmaps, etc. These documents often contain varying levels of sensitive information requiring access control based on employee roles (e.g., Engineer, HR, Product Manager). Traditional Q&A or RAG systems often struggle to handle such fine-grained permissions directly. Feeding all documents into a standard RAG system could lead to information leakage or users receiving irrelevant information they aren't authorized to see, reducing the system's utility and security.

**Task:**

My task was to design and develop a prototype system named "SecureRAG". The core objective was to build a LangChain-based RAG Q&A system capable of implementing **role-based data access control**. The specific requirement was that when receiving a user query, the system must consider the user's role, retrieve information *only* from documents the user is authorized to access, and generate answers based *only* on this authorized information, thereby ensuring the Q&A process is secure, accurate, and controlled.

**Action:**

To accomplish this task, I took the following series of actions:

1.  **Requirements Analysis & Design**:
    * Defined clear user roles (Engineer, HR, PM) and their corresponding document access permissions.
    * Designed a document metadata structure, explicitly including a `permission` field to store the list of allowed roles.
    * Planned the system's tech stack (Python, LangChain, Google Gemini/AI, FAISS, Streamlit).

2.  **Data Preparation & Indexing**:
    * Prepared sample documents (`data/docs.json`) containing different permission tags.
    * Developed an indexing script (`app/indexing.py`): Used LangChain to load documents, chunk text, generate vectors using Google AI's embedding model, and store the text chunks along with their **permission metadata** vectors into a FAISS vector database.

3.  **Permission-Aware Retrieval**:
    * Developed a custom `PermissionRetriever` class (`app/retriever.py`). After performing a standard vector similarity search, this retriever adds a **crucial filtering step**: it checks the metadata of each retrieved document chunk and retains only those whose `permission` list includes the current querying user's role.

4.  **RAG Chain Construction**:
    * Developed the core Q&A chain (`app/rag_chain.py`):
        * Used LangChain Expression Language (LCEL) to orchestrate the flow.
        * Integrated the `PermissionRetriever` to fetch permission-filtered context.
        * Utilized Google Gemini (`ChatGoogleGenerativeAI`) as the language model.
        * Designed a prompt template explicitly instructing the LLM to answer **solely based on** the provided context, and to state "I don't know" if the context is empty (due to lack of permission or relevance).

5.  **Testing & Validation**:
    * Wrote separate test scripts (`tests/test_retriever.py`, `tests/test_rag_chain.py`) to verify both the retriever's filtering logic and the end-to-end RAG chain's behavior under different role queries.

6.  **User Interface**:
    * Built a simple web UI using Streamlit (`ui/interface.py`) allowing users to select a role, input questions, and view the RAG system's responses, visually demonstrating the permission control effect.

7.  **Engineering Practices**:
    * Used virtual environments for dependency management (`requirements.txt`).
    * Managed API keys securely using `.env` files and `.gitignore`.
    * Documented the project with `README.md` and project status files.

**Result:**

* Successfully delivered a functional SecureRAG system prototype that effectively demonstrates how to integrate and enforce role-based access control within a RAG pipeline.
* Script-based testing and manual UI testing confirmed that the system accurately retrieves information from authorized documents based on the selected role and generates appropriate answers, preventing information leakage from restricted documents.
* The project demonstrated the practical application of key AI technologies like LangChain, vector databases, large language models (Gemini), and specific business logic (data permissions) to solve real-world security needs.
* The project code is well-structured, modular, and clearly documented (`README.md`, `PROJECT_STATUS.md`), providing a solid foundation for future iteration or deployment.
* This project experience demonstrates my ability to design, develop, and test complex AI applications involving specific business logic like access control.
