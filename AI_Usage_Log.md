# AI使用日志

## 项目名称
基于本地知识库的RAG智能问答系统

## 使用的AI工具
- Trae AI 编程助手
- GitHub Copilot（辅助生成代码）

---

## AI提问日志

### 1. 项目架构设计
**提问时间**: 2026-06-01
**问题**: 如何设计一个基于Ollama + LangChain + Streamlit的RAG系统架构？需要包含哪些模块？
**AI回答摘要**: 建议分为知识库模块（文档加载、分块、向量化）、RAG问答链模块（提示词、检索、生成）、Web界面模块（Streamlit交互），并提供了模块间的调用关系图。
**代码影响**: 确定了项目分为 knowledge_base.py、rag_chain.py、app.py 三个核心模块。

---

### 2. 文档加载器实现
**提问时间**: 2026-06-01
**问题**: LangChain中如何同时支持PDF和DOCX格式的文档加载？需要处理哪些异常？
**AI回答摘要**: 使用PyPDFLoader和Docx2txtLoader，需要做文件存在性校验、格式校验、编码异常处理。
**代码影响**: knowledge_base.py 中的 load_single_document() 和 load_from_bytes() 方法。

---

### 3. 文本分块策略
**提问时间**: 2026-06-01
**问题**: 中文文档的RecursiveCharacterTextSplitter应该如何配置？chunk_size和chunk_overlap设置多少合适？
**AI回答摘要**: 中文分块建议使用["\n\n", "\n", "。", "！", "？", " ", ""]作为分隔符，chunk_size=1000，chunk_overlap=200。
**代码影响**: knowledge_base.py 中的 split_documents() 方法的参数配置。

---

### 4. Ollama嵌入模型集成
**提问时间**: 2026-06-01
**问题**: 如何在LangChain中使用Ollama的nomic-embed-text嵌入模型？需要什么配置？
**AI回答摘要**: 使用OllamaEmbeddings类，指定model参数为"nomic-embed-text"，确保Ollama服务已启动且模型已下载。
**代码影响**: knowledge_base.py 中的 embeddings 初始化。

---

### 5. ConversationalRetrievalChain配置
**提问时间**: 2026-06-01
**问题**: LangChain的ConversationalRetrievalChain如何配置系统提示词和对话记忆？
**AI回答摘要**: 使用from_llm方法，通过combine_docs_chain_kwargs传入自定义prompt，配置ConversationBufferMemory。
**代码影响**: rag_chain.py 中的 _build_chain() 方法和提示词模板。

---

### 6. 系统提示词设计
**提问时间**: 2026-06-01
**问题**: 如何设计RAG系统的系统提示词，要求模型基于文档回答，无答案时明确拒绝？
**AI回答摘要**: 提示词需要明确规则：1.仅使用参考文档 2.无信息时说"文档中未找到相关答案" 3.不编造信息。
**代码影响**: rag_chain.py 中的 QA_PROMPT_TEMPLATE。

---

### 7. Streamlit会话状态管理
**提问时间**: 2026-06-01
**问题**: Streamlit中如何管理知识库实例和对话历史，避免每次刷新重新初始化？
**AI回答摘要**: 使用st.session_state存储kb、rag、messages等对象，在init_session_state()中统一初始化。
**代码影响**: app.py 中的 init_session_state() 函数和所有状态管理逻辑。

---

### 8. Streamlit文件上传处理
**提问时间**: 2026-06-01
**问题**: Streamlit上传的文件如何传递给LangChain的文档加载器？需要临时文件吗？
**AI回答摘要**: 使用getvalue()获取字节流，写入NamedTemporaryFile，再调用加载器，最后删除临时文件。
**代码影响**: knowledge_base.py 中的 load_from_bytes() 方法。

---

### 9. Streamlit聊天界面实现
**提问时间**: 2026-06-01
**问题**: 如何用Streamlit实现类似ChatGPT的聊天界面？需要显示历史消息和参考来源。
**AI回答摘要**: 使用st.chat_message()显示消息，st.chat_input()获取输入，将消息存入session_state，用expander显示参考来源。
**代码影响**: app.py 中的 display_chat_message() 函数和主界面循环。

---

### 10. PyInstaller打包Streamlit应用
**提问时间**: 2026-06-01
**问题**: 如何用PyInstaller将Streamlit应用打包成exe？需要处理哪些依赖和数据文件？
**AI回答摘要**: 需要--collect-all收集所有依赖，--add-data添加streamlit资源，编写runtime-hook启动脚本。
**代码影响**: build.bat 和 run_streamlit.py。

---

## AI生成代码统计

| 模块文件 | AI生成比例 | 主要生成内容 |
|---------|-----------|-------------|
| knowledge_base.py | 70% | 文档加载类、分块逻辑、向量数据库操作 |
| rag_chain.py | 75% | 系统提示词设计、ConversationalRetrievalChain集成 |
| app.py | 80% | Streamlit界面布局、状态管理、交互逻辑 |
| cli_qa.py | 60% | 主流程控制和交互逻辑 |
| test_ollama.py | 90% | API测试逻辑和结果展示 |
| build.bat | 95% | PyInstaller打包配置和命令 |
| run_streamlit.py | 90% | PyInstaller运行时钩子 |

## 代码修改记录
- 所有AI生成的代码都经过人工审查和修改
- 调整了中文分块的分隔符顺序，优化了分块效果
- 增加了文件路径校验和异常处理的中文提示
- 优化了Streamlit界面的布局和用户体验
- 添加了详细的代码注释和类型注解

## 遇到的问题与解决方案
1. **问题**: LangChain导入错误 - 版本不兼容
   **解决方案**: 固定langchain==0.1.10, langchain-community==0.0.25, langchain-core==0.1.28版本
   
2. **问题**: ChromaDB持久化路径问题
   **解决方案**: 手动创建persist_directory，使用绝对路径

3. **问题**: Streamlit刷新后状态丢失
   **解决方案**: 使用st.session_state统一管理所有会话状态

---

## 备注
- AI主要用于代码骨架生成和常见问题解答
- 核心业务逻辑和架构设计由人工完成
- 所有AI生成代码都经过理解和适当修改