# secure-rag/tests/test_retriever.py

import os
import sys
import argparse

# Add project root directory to Python path to allow importing 'app' module
# __file__ is the path to the current script (test_retriever.py)
# os.path.dirname(__file__) is the tests/ directory
# os.path.join(..., '..') is the parent directory of tests/, which is secure-rag/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now we can import from the 'app' directory
from app.retriever import PermissionRetriever

# Load .env file located in the project root directory
# load_dotenv() automatically searches for .env in current or parent directories
from dotenv import load_dotenv
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    # Specify the path to the .env file for loading
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded environment variables from {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}. GOOGLE_API_KEY might not be set.")


# --- Test Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the PermissionRetriever.") # 测试 PermissionRetriever
    parser.add_argument("--role", type=str, required=True, choices=['HR', 'Engineer', 'PM'], help="User role for testing.") # 用于测试的用户角色
    parser.add_argument("--query", type=str, default="What is the policy on remote work?", help="Query to test.") # 要测试的查询
    # The vector store path is handled internally by the PermissionRetriever class,
    # which looks for ../vectorstore relative to app/retriever.py.
    # We don't need to specify the path here unless overriding defaults.

    args = parser.parse_args()

    # Ensure the API key is loaded
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("错误: GOOGLE_API_KEY 环境变量未设置。请确保它在项目根目录的 .env 文件中。") # Error: GOOGLE_API_KEY environment variable not set. Please ensure it's in the .env file in the project root.
        sys.exit(1) # Exit the script
    # Optional: Print a confirmation that the key was found (without printing the key itself)
    # print("GOOGLE_API_KEY found in environment.")

    try:
        print(f"Initializing retriever...")
        # Use the default path settings within PermissionRetriever
        retriever = PermissionRetriever()

        # Get relevant documents
        print(f"Running query for role '{args.role}'...")
        relevant_docs = retriever.get_relevant_documents(args.query, args.role)

        # Print results
        if relevant_docs:
            print("\n--- Filtered Relevant Documents (过滤后的相关文档) ---")
            for i, doc in enumerate(relevant_docs):
                print(f"\nDocument {i+1}:")
                print(f"  Title (标题): {doc.metadata.get('title', 'N/A')}")
                print(f"  Content Snippet (内容片段): {doc.page_content[:150]}...")
                print(f"  Allowed Roles (允许的角色): {doc.metadata.get('permission', 'N/A')}")
        else:
            print("\nNo relevant documents found for this role and query. (未找到此角色和查询的相关文档)")

    except FileNotFoundError as e:
        print(f"\n错误 (Error): {e}")
        print("请确保你已经运行了 app/indexing.py 并且 vectorstore 目录存在于 secure-rag/vectorstore。") # Please ensure you have run app/indexing.py and the vectorstore directory exists at secure-rag/vectorstore.
    except Exception as e:
        print(f"\n发生意外错误 (An unexpected error occurred): {e}")

