# secure-rag/app/retriever.py

import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document # 用于类型提示

# 加载 .env 文件中的环境变量 (例如 GOOGLE_API_KEY)
# 确保 .env 文件在项目根目录中
from dotenv import load_dotenv
load_dotenv()

# --- 配置 ---
VECTORSTORE_PATH = "../vectorstore" # 相对于此脚本的路径 (app/)
GOOGLE_EMBEDDING_MODEL = "models/embedding-001" # 必须与 indexing.py 中使用的模型匹配

class PermissionRetriever:
    """
    一个根据文档元数据中存储的用户权限过滤文档的检索器。
    """
    def __init__(self, vectorstore_path: str = VECTORSTORE_PATH, embedding_model_name: str = GOOGLE_EMBEDDING_MODEL):
        """
        通过加载向量存储来初始化检索器。

        Args:
            vectorstore_path: 保存的 FAISS 索引目录的路径。
            embedding_model_name: 索引时使用的嵌入模型的名称。
        """
        # 调整路径，使其相对于当前文件位置的父目录中的 vectorstore
        # 如果 vectorstore_path 是相对路径，则基于当前文件的目录进行解析
        if not os.path.isabs(vectorstore_path):
             # 获取当前脚本文件所在的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建相对于当前脚本的绝对路径
            vectorstore_path = os.path.join(current_dir, vectorstore_path)
            vectorstore_path = os.path.normpath(vectorstore_path) # 规范化路径 (处理 ../)


        print(f"Attempting to load vector store from: {vectorstore_path}") # 调试信息

        if not os.path.exists(vectorstore_path) or not os.path.isdir(vectorstore_path):
            raise FileNotFoundError(f"在 {vectorstore_path} 找不到向量存储目录。请确保路径正确并且已运行 indexing.py。")

        try:
            # 初始化用于索引的相同嵌入函数
            # GOOGLE_API_KEY 应已通过 load_dotenv() 从 .env 文件加载
            embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name)
        except Exception as e:
            print(f"初始化 Google Embeddings 时出错。请确保 GOOGLE_API_KEY 在 .env 文件中设置正确。错误: {e}")
            raise # 重新引发异常以停止初始化

        try:
            # 加载 FAISS 向量存储
            self.vectorstore = FAISS.load_local(
                vectorstore_path,
                embeddings,
                allow_dangerous_deserialization=True # 为兼容性添加
            )
            print(f"成功从 {vectorstore_path} 加载向量存储")
        except Exception as e:
            print(f"从 {vectorstore_path} 加载向量存储时出错: {e}")
            raise # 重新引发

    def get_relevant_documents(self, query: str, user_role: str, k: int = 4) -> list[Document]:
        """
        检索与查询相关的文档，并根据用户角色对其进行过滤。

        Args:
            query: 用户的问题。
            user_role: 发出查询的用户的角色 (例如 'HR', 'Engineer', 'PM')。
            k: 在过滤前最初检索的文档数。

        Returns:
            一个与用户相关且用户可访问的 LangChain Document 对象列表。
        """
        if not self.vectorstore:
            print("错误: 向量存储未加载。")
            return []

        print(f"\n--- 正在为角色检索: {user_role} ---")
        print(f"查询: {query}")

        # 1. 执行相似性搜索
        try:
            potential_matches = self.vectorstore.similarity_search(query, k=k)
            print(f"找到 {len(potential_matches)} 个潜在匹配项 (过滤前)。")
        except Exception as e:
            print(f"相似性搜索期间出错: {e}")
            return []

        # 2. 根据 user_role 和文档元数据过滤结果
        filtered_docs = []
        for doc in potential_matches:
            if 'permission' in doc.metadata:
                allowed_roles = doc.metadata['permission']
                if user_role in allowed_roles:
                    filtered_docs.append(doc)
            else:
                print(f"警告: 文档 '{doc.metadata.get('title', 'N/A')}' 缺少 'permission' 元数据。拒绝访问。")
                pass

        print(f"权限过滤后返回 {len(filtered_docs)} 个文档。")
        return filtered_docs
