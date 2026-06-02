"""
Streamlit Web应用主入口：RAG智能问答系统
AI生成部分：Streamlit界面布局、状态管理、交互逻辑由AI辅助生成
"""

import os
import sys
import time
import streamlit as st

from knowledge_base import KnowledgeBase
from rag_chain import RAGChain


st.set_page_config(
    page_title="RAG智能问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """初始化会话状态"""
    if "kb" not in st.session_state:
        st.session_state.kb = KnowledgeBase(
            persist_directory="chroma_db",
            embedding_model="nomic-embed-text",
            llm_model="deepseek-r1:7b",
            chunk_size=1000,
            chunk_overlap=200
        )
        st.session_state.kb.load_existing_vector_store()
    
    if "rag" not in st.session_state:
        st.session_state.rag = RAGChain(
            llm_model="deepseek-r1:7b",
            temperature=0.1,
            top_k=3
        )
        if st.session_state.kb.vector_store is not None:
            st.session_state.rag.set_vector_store(st.session_state.kb.vector_store)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    if "pending_files" not in st.session_state:
        st.session_state.pending_files = []


def clear_chat_history():
    """清空对话历史"""
    st.session_state.messages = []
    if "rag" in st.session_state:
        st.session_state.rag.clear_memory()


def get_kb_stats():
    """获取知识库统计信息"""
    if "kb" in st.session_state:
        return st.session_state.kb.get_stats()
    return {"total_documents": 0, "total_chunks": 0, "vector_store_exists": False}


def process_uploaded_files(uploaded_files):
    """处理上传的文件"""
    kb = st.session_state.kb
    all_documents = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"正在处理: {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
        progress_bar.progress((i) / len(uploaded_files))
        
        try:
            file_bytes = uploaded_file.getvalue()
            documents = kb.load_from_bytes(uploaded_file.name, file_bytes)
            all_documents.extend(documents)
            st.session_state.uploaded_files.append(uploaded_file.name)
        except Exception as e:
            st.error(f"处理 {uploaded_file.name} 时出错: {e}")
    
    progress_bar.progress(1.0)
    status_text.text(f"文档处理完成，共加载 {len(all_documents)} 个文档")
    
    return all_documents


def build_or_update_knowledge_base(documents):
    """构建或更新知识库"""
    kb = st.session_state.kb
    rag = st.session_state.rag
    
    if kb.vector_store is None:
        with st.spinner("正在构建向量数据库..."):
            vector_store = kb.build_vector_store(documents)
            rag.set_vector_store(vector_store)
            st.success(f"知识库构建完成！共 {len(documents)} 个文档")
    else:
        with st.spinner("正在更新向量数据库..."):
            vector_store = kb.update_vector_store(documents)
            rag.set_vector_store(vector_store)
            st.success(f"知识库更新完成！新增 {len(documents)} 个文档")
    
    st.session_state.pending_files = []


def display_chat_message(role, content, sources=None):
    """显示聊天消息"""
    with st.chat_message(role):
        st.markdown(content)
        
        if sources and role == "assistant":
            with st.expander("查看参考来源", expanded=False):
                for i, doc in enumerate(sources, 1):
                    source = doc.metadata.get("source", "未知")
                    st.markdown(f"**[{i}] {source}**")
                    st.markdown(f"> {doc.page_content[:200]}...")


def main():
    init_session_state()
    
    with st.sidebar:
        st.title("🤖 RAG智能问答系统")
        st.markdown("---")
        
        st.subheader("📁 文档上传")
        uploaded_files = st.file_uploader(
            "上传PDF、DOCX或TXT文档",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="支持批量上传，文件大小不超过200MB"
        )
        
        if uploaded_files:
            current_files = {f.name for f in uploaded_files}
            pending_files = [f for f in uploaded_files if f.name not in st.session_state.uploaded_files]
            st.session_state.pending_files = pending_files
            
            if pending_files:
                st.info(f"待处理文件: {len(pending_files)} 个")
            else:
                st.success("所有文件已处理")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔧 构建知识库", use_container_width=True, disabled=not st.session_state.pending_files):
                if st.session_state.pending_files:
                    documents = process_uploaded_files(st.session_state.pending_files)
                    if documents:
                        build_or_update_knowledge_base(documents)
        
        with col2:
            if st.button("🗑️ 清空知识库", use_container_width=True):
                if st.button("确认清空", key="confirm_clear"):
                    st.session_state.kb.clear()
                    st.session_state.uploaded_files = []
                    st.session_state.pending_files = []
                    st.session_state.rag = RAGChain(
                        llm_model="deepseek-r1:7b",
                        temperature=0.1,
                        top_k=3
                    )
                    clear_chat_history()
                    st.success("知识库已清空")
        
        st.markdown("---")
        st.subheader("📊 知识库状态")
        
        stats = get_kb_stats()
        col3, col4 = st.columns(2)
        with col3:
            st.metric("文档数", stats["total_documents"])
        with col4:
            st.metric("文本块数", stats["total_chunks"])
        
        if stats["vector_store_exists"]:
            st.success("向量数据库已就绪")
        else:
            st.warning("请先上传文档并构建知识库")
        
        if st.session_state.uploaded_files:
            with st.expander("已上传文件列表", expanded=False):
                for f in st.session_state.uploaded_files:
                    st.markdown(f"- {f}")
        
        st.markdown("---")
        st.subheader("⚡ 快捷操作")
        
        if st.button("📂 从docs目录加载文档", use_container_width=True):
            docs_dir = "docs"
            if os.path.exists(docs_dir):
                import glob
                docx_files = glob.glob(os.path.join(docs_dir, "*.docx"))
                pdf_files = glob.glob(os.path.join(docs_dir, "*.pdf"))
                txt_files = glob.glob(os.path.join(docs_dir, "*.txt"))
                all_files = docx_files + pdf_files + txt_files
                
                if all_files:
                    class MockUploadedFile:
                        def __init__(self, file_path):
                            self.name = os.path.basename(file_path)
                            self._file_path = file_path
                        def getvalue(self):
                            with open(self._file_path, 'rb') as f:
                                return f.read()
                    
                    mock_files = [MockUploadedFile(f) for f in all_files]
                    current_files = {f.name for f in mock_files}
                    pending_files = [f for f in mock_files if f.name not in st.session_state.uploaded_files]
                    
                    if pending_files:
                        st.session_state.pending_files = pending_files
                        st.success(f"发现 {len(pending_files)} 个待处理文件")
                        documents = process_uploaded_files(pending_files)
                        if documents:
                            build_or_update_knowledge_base(documents)
                    else:
                        st.info("所有文件已处理")
                else:
                    st.warning("docs目录中没有找到文档")
            else:
                st.error("docs目录不存在")
        
        st.markdown("---")
        
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            clear_chat_history()
            st.success("对话历史已清空")
        
        st.markdown("---")
        st.caption("💡 基于Ollama + LangChain + Streamlit构建")
    
    st.title("💬 智能问答")
    st.markdown("---")
    
    for message in st.session_state.messages:
        display_chat_message(
            message["role"],
            message["content"],
            message.get("sources")
        )
    
    if prompt := st.chat_input("请输入您的问题..."):
        display_chat_message("user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                result = st.session_state.rag.ask(prompt)
                answer = result["answer"]
                sources = result.get("source_documents", [])
                
                st.markdown(answer)
                
                if sources:
                    with st.expander("查看参考来源", expanded=False):
                        for i, doc in enumerate(sources, 1):
                            source = doc.metadata.get("source", "未知")
                            st.markdown(f"**[{i}] {source}**")
                            st.markdown(f"> {doc.page_content[:200]}...")
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })
    
    if not st.session_state.messages:
        st.info("👋 您好！请先在左侧上传文档并构建知识库，然后开始提问。")
        st.markdown("""
        ### 功能说明
        - 📄 **文档上传**：支持PDF和DOCX格式，可批量上传
        - 🔧 **知识库构建**：自动解析、分块、向量化文档
        - 💬 **智能问答**：基于知识库内容回答问题
        - 📚 **来源显示**：可查看答案参考的文档片段
        - 🧠 **会话记忆**：支持多轮上下文对话
        """)


if __name__ == "__main__":
    main()