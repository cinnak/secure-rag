### SecureRAG 项目 STAR 框架叙述

**Situation (情境):**

在一个典型的公司（比如我们模拟的 "AI Tech Solutions Inc."）内部，存在大量的知识文档，例如技术规范、HR 政策、产品路线图等。这些文档往往包含不同层级的敏感信息，需要根据员工的角色（如工程师、HR、产品经理）进行访问控制。传统的知识问答或 RAG 系统通常难以直接处理这种细粒度的权限问题，如果直接将所有文档喂给 RAG 系统，可能会导致信息泄露，或者用户得到与其工作无关、甚至无权查看的信息，降低了系统的实用性和安全性。

**Task (任务):**

我的任务是设计并开发一个名为 "SecureRAG" 的原型系统。核心目标是构建一个基于 LangChain 的 RAG 问答系统，该系统必须能够实现**基于用户角色的数据权限控制**。具体要求是：系统在接收用户问题时，必须同时考虑用户的角色，仅从该用户有权访问的文档中检索信息，并基于这些授权信息生成回答，从而确保问答过程的安全、精准和可控。

**Action (行动):**

为了完成这个任务，我采取了以下一系列行动：

1.  **需求分析与设计**:
    * 定义了清晰的用户角色（Engineer, HR, PM）及其对应的文档访问权限。
    * 设计了文档元数据结构，在其中明确加入了 `permission` 字段来存储允许访问的角色列表。
    * 规划了系统的技术栈（Python, LangChain, Google Gemini/AI, FAISS, Streamlit）。

2.  **数据准备与索引**:
    * 准备了包含不同权限标签的示例文档 (`data/docs.json`)。
    * 开发了索引脚本 (`app/indexing.py`)：使用 LangChain 加载文档，进行文本分块，调用 Google AI 的 embedding 模型生成向量，并将文本块及其包含**权限元数据**的向量存储到 FAISS 向量数据库中。

3.  **权限感知检索**:
    * 开发了自定义的 `PermissionRetriever` 类 (`app/retriever.py`)。这个检索器在执行标准的向量相似性搜索后，会**关键性地增加一个过滤步骤**：检查每个检索到的文档块的元数据，只保留那些 `permission` 列表包含当前查询用户角色的文档块。

4.  **RAG 链构建**:
    * 开发了核心的问答链 (`app/rag_chain.py`)：
        * 使用 LangChain 表达式语言 (LCEL) 编排流程。
        * 集成了 `PermissionRetriever` 来获取经过权限过滤的上下文。
        * 调用 Google Gemini (`ChatGoogleGenerativeAI`) 作为语言模型。
        * 设计了 Prompt 模板，明确指示 LLM 必须**仅基于**提供的上下文回答问题，如果上下文为空（因为权限不足或无相关内容）则回答不知道。

5.  **测试验证**:
    * 编写了独立的测试脚本 (`tests/test_retriever.py`, `tests/test_rag_chain.py`)，分别验证了权限检索器的过滤逻辑和整个 RAG 链在不同角色查询下的端到端行为。

6.  **用户界面**:
    * 使用 Streamlit (`ui/interface.py`) 构建了一个简单的 Web UI，允许用户选择角色、输入问题，并查看 RAG 系统返回的答案，直观地展示了权限控制的效果。

7.  **工程实践**:
    * 使用了虚拟环境进行依赖管理 (`requirements.txt`)。
    * 通过 `.env` 文件和 `.gitignore` 安全地管理 API 密钥。
    * 编写了 `README.md` 和项目状态文档进行记录。

**Result (结果):**

* 成功交付了一个功能完备的 SecureRAG 系统原型，该原型有效地演示了如何在 RAG 流程中集成并强制执行基于角色的访问控制。
* 通过脚本测试和 UI 手动测试验证，系统能够根据用户选择的角色，准确地从授权文档中检索信息并生成回答，对于无权访问的信息则不会返回相关内容，有效避免了信息泄露。
* 该项目实践了 LangChain、向量数据库、大型语言模型（Gemini）等关键 AI 技术在解决实际业务安全需求（数据权限）方面的应用。
* 项目代码结构清晰、模块化，并且有良好的文档记录 (`README.md`, `PROJECT_STATUS.md`)，为后续的迭代开发或实际部署打下了良好基础。
* 这个项目经验证明了我具备设计、开发和测试带有特定业务逻辑（如权限控制）的复杂 AI 应用的能力。
