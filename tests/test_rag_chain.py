import os
import sys

# 将项目根目录添加到 Python 路径，以便导入 app 模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# 从 app 模块导入核心函数
# 这会执行 app/rag_chain.py 中的代码，包括初始化
try:
    from app.rag_chain import get_rag_response
    print("Successfully imported get_rag_response from app.rag_chain")
except ImportError as e:
    print(f"Error importing from app.rag_chain: {e}")
    print("Ensure app/rag_chain.py exists and has no syntax errors.")
    sys.exit(1)
except FileNotFoundError as e: # 捕获由 retriever 初始化抛出的 FileNotFoundError
     print(f"Error during import (likely retriever init failed): {e}")
     sys.exit(1)
except Exception as e: # 捕获其他可能的导入时初始化错误
     print(f"Unexpected error during import: {e}")
     sys.exit(1)



if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
         print("错误: GOOGLE_API_KEY 环境变量未设置。请确保它在项目根目录的 .env 文件中。")
         sys.exit(1)

    print("\n--- Testing RAG Chain ---")

    # --- Test Cases ---
    test_cases = [
        {"role": "Engineer", "query": "How is the LangChain service deployed?"},
        {"role": "HR", "query": "How is the LangChain service deployed?"}, # Expect denial/no context
        {"role": "HR", "query": "What is the bonus structure?"},
        {"role": "Engineer", "query": "What is the bonus structure?"}, # Expect denial/no context
        {"role": "PM", "query": "What is the remote work policy?"} # Accessible to all
    ]

    all_passed = True # Simple flag, can be expanded with assertions
    for i, case in enumerate(test_cases):
        role = case["role"]
        query = case["query"]
        print(f"\n--- Test Case {i+1} ---")
        print(f"User Role: {role}")
        print(f"Query: {query}")

        # 调用 RAG 链函数
        answer = get_rag_response(query, role)

        print(f"Answer:\n{answer}")


        # Example basic check (can be made more robust)
        if role == "HR" and "deploy" in query and "know" not in answer.lower() and "context" in answer.lower():
             print("Potential Failure: HR might have received deployment info?")
             all_passed = False
        elif role == "Engineer" and "bonus" in query and "know" not in answer.lower() and "context" in answer.lower():
             print("Potential Failure: Engineer might have received bonus info?")
             all_passed = False


    print("\n--- Testing Finished ---")
    if all_passed:
        print("All basic checks passed (manual verification needed).")
    else:
        print("Some checks failed.")

