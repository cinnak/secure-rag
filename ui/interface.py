# secure-rag/ui/interface.py

import streamlit as st
import os
import sys

# --- Path Setup ---
# 将项目根目录添加到 Python 路径，以便可以导入 app 模块
# __file__ 是当前脚本 (interface.py) 的路径
# os.path.dirname(__file__) 是 ui/ 目录
# os.path.join(..., '..') 是 ui/ 的父目录，即 secure-rag/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# --- Import RAG Chain Function ---
# 导入会执行 app/rag_chain.py 中的初始化代码
try:
    # 确保环境变量在导入前已设置（由 .env 文件处理）
    # 如果 rag_chain.py 没有成功加载 .env，这里可能会在初始化时出错
    from app.rag_chain import get_rag_response
    print("Successfully imported get_rag_response from app.rag_chain")
    RAG_AVAILABLE = True
except ImportError as e:
    st.error(f"无法导入 RAG 链模块: {e}. 请确保 app/rag_chain.py 存在且无误。")
    RAG_AVAILABLE = False
except FileNotFoundError as e: # 捕获向量存储加载错误
     st.error(f"初始化 RAG 链时出错 (可能找不到向量存储): {e}")
     RAG_AVAILABLE = False
except Exception as e: # 捕获其他初始化错误 (例如 API Key 问题)
     st.error(f"初始化 RAG 链时发生意外错误: {e}. 请检查 .env 文件和 API 密钥。")
     RAG_AVAILABLE = False

# --- Streamlit App ---

# 设置页面标题
st.set_page_config(page_title="SecureRAG Q&A", layout="wide")
st.title("🔒 SecureRAG: 基于权限的知识问答系统")

# --- User Inputs ---
st.sidebar.header("用户设置")

# 1. 角色选择 (模拟登录)
available_roles = ['Engineer', 'HR', 'PM']
selected_role = st.sidebar.selectbox(
    "选择你的角色:",
    options=available_roles,
    index=0 # 默认选择第一个角色
)
st.sidebar.info(f"当前角色: **{selected_role}**")

# 2. 问题输入
st.header("提出你的问题")
user_query = st.text_area("在这里输入你的问题:", height=100, key="query_input")

# 3. 提交按钮
submit_button = st.button("提交问题", key="submit_button", disabled=not RAG_AVAILABLE)

# --- Display Answer ---
st.header("回答")

if submit_button and RAG_AVAILABLE:
    if user_query:
        # 显示加载状态
        with st.spinner(f"正在以 **{selected_role}** 身份查找答案..."):
            try:
                # 调用 RAG 链获取答案
                answer = get_rag_response(user_query, selected_role)

                # 显示答案
                st.markdown(answer) # 使用 markdown 以便格式化 (例如换行)
            except Exception as e:
                st.error(f"处理请求时发生错误: {e}")
    else:
        st.warning("请输入你的问题。")
elif not RAG_AVAILABLE:
     st.error("RAG 问答链不可用，请检查后台错误或配置。")

# --- Footer or Additional Info (Optional) ---
st.markdown("---")
st.caption("AI Tech Solutions Inc. 内部知识库")

