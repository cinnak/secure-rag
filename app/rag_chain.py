# secure-rag/app/rag_chain.py

import os
from operator import itemgetter # 用于 LCEL 链操作

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document # 用于类型提示

# 导入自定义检索器
# 确保 retriever.py 在同一目录或 Python 路径已正确设置
# 注意：如果 PermissionRetriever 依赖 .env, 它内部的 load_dotenv() 会处理
from .retriever import PermissionRetriever

# 在此脚本的顶层也加载 .env 文件，以确保环境变量可用
# (如果 PermissionRetriever 内部也加载，重复加载通常无害)
from dotenv import load_dotenv
load_dotenv()
print("Attempted to load .env file from rag_chain.py")


# --- 配置 ---
# 假设 GOOGLE_API_KEY 已通过 .env 加载
VECTORSTORE_PATH = "../vectorstore" # 相对于此脚本 (app/) 的路径
GOOGLE_EMBEDDING_MODEL = "models/embedding-001"
# 使用你验证过的可用模型名称
GOOGLE_CHAT_MODEL = "gemini-2.5-pro-exp-03-25"

# --- 辅助函数：格式化文档 ---
def format_docs(docs: list[Document]) -> str:
    """将 Document 对象列表转换为单个字符串。"""
    return "\n\n".join(doc.page_content for doc in docs)

# --- RAG 链实现 ---

# 1. 初始化检索器
# PermissionRetriever 的 __init__ 现在处理路径解析
try:
    # 传递相对于此脚本位置的路径
    retriever = PermissionRetriever(vectorstore_path=VECTORSTORE_PATH, embedding_model_name=GOOGLE_EMBEDDING_MODEL)
except FileNotFoundError as e:
    print(f"初始化检索器时出错: {e}")
    print("请确保向量存储在指定路径存在。")
    retriever = None
except Exception as e:
    print(f"检索器初始化期间发生意外错误: {e}")
    retriever = None

# 2. 初始化聊天模型
try:
    llm = ChatGoogleGenerativeAI(model=GOOGLE_CHAT_MODEL, temperature=0, convert_system_message_to_human=True)
    # temperature=0 使回答更具确定性
    # convert_system_message_to_human=True 可能对某些 Gemini 提示结构有帮助
except Exception as e:
    print(f"初始化 Google Chat 模型时出错 (使用 {GOOGLE_CHAT_MODEL}): {e}")
    print("请确保 GOOGLE_API_KEY 有效且模型名称正确。")
    llm = None

# 3. 定义提示模板
template = """
You are an assistant for question-answering tasks for 'AI Tech Solutions Inc.'.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Keep the answer concise and based *only* on the provided context.

Context:
{context}

Question:
{question}

Answer:"""
prompt = ChatPromptTemplate.from_template(template)

# 4. 构建 RAG 链 (使用 LCEL)

rag_chain = None # 初始化为 None
if retriever and llm:
    # 用于将查询和角色传递给检索器的函数
    def retrieve_documents(input_dict):
        return retriever.get_relevant_documents(
            query=input_dict["query"],
            user_role=input_dict["user_role"]
        )

    # 定义使用 RunnableParallel 和序列操作符 | 的步骤
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["documents"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    # 主要的链结构
    rag_chain = RunnableParallel(
        {
            "documents": retrieve_documents, # 基于查询和角色检索文档
            "question": itemgetter("query") # 直接传递原始查询
        }
    ).assign(answer=rag_chain_from_docs) # 将检索到的文档和问题传递给最终步骤

    print("RAG chain created successfully.")
else:
    print("由于初始化错误，无法创建 RAG 链。")


# --- 获取响应的函数 ---
def get_rag_response(query: str, user_role: str) -> str:
    """
    为给定的查询和用户角色从 RAG 链获取响应。

    Args:
        query: 用户的问题。
        user_role: 用户的角色 ('HR', 'Engineer', 'PM')。

    Returns:
        生成的答案字符串，或错误消息。
    """
    if not rag_chain:
        return "错误: RAG 链不可用。"

    try:
        # 链期望一个包含 'query' 和 'user_role' 的字典
        response = rag_chain.invoke({"query": query, "user_role": user_role})
        # 我们想要的最终输出在 'answer' 键中
        return response.get("answer", "错误: 无法从链响应中解析答案。")
    except Exception as e:
        # 如果可能，更具体地说明潜在的 API 错误
        return f"RAG 链调用期间发生错误: {e}"

# 注意：此文件现在只包含核心逻辑和 get_rag_response 函数。
# 测试/示例用法已移至单独的脚本 (例如 tests/test_rag_chain.py)。
