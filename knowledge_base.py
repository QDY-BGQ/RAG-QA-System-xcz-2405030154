"""
知识库构建模块：实现文档加载、文本分割、向量化存储和检索功能
AI生成部分：文档加载类、文本分块逻辑、向量数据库操作由AI辅助生成
"""

import os
from typing import List, Optional
from pathlib import Path

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader


class KnowledgeBase:
    """知识库管理类，负责文档加载、分块、向量化和检索"""
    
    def __init__(
        self,
        persist_directory: str = "chroma_db",
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "deepseek-r1:7b",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        初始化知识库
        
        Args:
            persist_directory: 向量数据库持久化目录
            embedding_model: 嵌入模型名称
            llm_model: 大语言模型名称
            chunk_size: 文本分块大小
            chunk_overlap: 分块重叠大小
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.vector_store: Optional[Chroma] = None
        self.documents: List[Document] = []
        
        os.makedirs(persist_directory, exist_ok=True)
    
    def load_documents_from_folder(self, folder_path: str) -> List[Document]:
        """
        从文件夹批量加载文档
        
        Args:
            folder_path: 文档文件夹路径
            
        Returns:
            加载的文档列表
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
        
        documents = []
        folder = Path(folder_path)
        
        for file_path in folder.glob("**/*"):
            if file_path.is_file():
                try:
                    doc = self.load_single_document(str(file_path))
                    if doc:
                        documents.extend(doc)
                        print(f"✓ 已加载: {file_path.name}")
                except Exception as e:
                    print(f"✗ 加载 {file_path.name} 时出错: {e}")
        
        self.documents.extend(documents)
        return documents
    
    def load_single_document(self, file_path: str) -> List[Document]:
        """
        加载单个文档
        
        Args:
            file_path: 文档文件路径
            
        Returns:
            加载的文档列表
            
        Raises:
            ValueError: 不支持的文件格式
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif file_ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif file_ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}，仅支持PDF、DOCX和TXT")
        
        documents = loader.load()
        
        for doc in documents:
            doc.metadata["source"] = os.path.basename(file_path)
            doc.metadata["file_path"] = file_path
        
        return documents
    
    def load_from_bytes(self, file_name: str, file_bytes: bytes) -> List[Document]:
        """
        从字节流加载文档（用于Streamlit上传）
        
        Args:
            file_name: 文件名
            file_bytes: 文件字节内容
            
        Returns:
            加载的文档列表
        """
        import tempfile
        
        file_ext = os.path.splitext(file_name)[1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name
        
        try:
            documents = self.load_single_document(tmp_file_path)
        finally:
            os.unlink(tmp_file_path)
        
        for doc in documents:
            doc.metadata["source"] = file_name
        
        self.documents.extend(documents)
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        对文档进行分块处理
        
        Args:
            documents: 待分块的文档列表
            
        Returns:
            分块后的文档列表
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✓ 文档分块完成，共 {len(chunks)} 个文本块")
        return chunks
    
    def build_vector_store(self, documents: List[Document]) -> Chroma:
        """
        构建向量数据库
        
        Args:
            documents: 文档列表（可以是原始文档或分块后的文档）
            
        Returns:
            向量数据库实例
        """
        chunks = self.split_documents(documents)
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print(f"✓ 向量数据库构建完成，共 {len(chunks)} 个文本块")
        return self.vector_store
    
    def update_vector_store(self, new_documents: List[Document]) -> Chroma:
        """
        更新向量数据库（添加新文档）
        
        Args:
            new_documents: 新添加的文档列表
            
        Returns:
            更新后的向量数据库实例
        """
        chunks = self.split_documents(new_documents)
        
        if self.vector_store is None:
            self.vector_store = self.build_vector_store(new_documents)
        else:
            self.vector_store.add_documents(chunks)
            print(f"✓ 向量数据库更新完成，新增 {len(chunks)} 个文本块")
        
        return self.vector_store
    
    def load_existing_vector_store(self) -> Optional[Chroma]:
        """
        加载已存在的向量数据库
        
        Returns:
            向量数据库实例，如果不存在则返回None
        """
        if os.path.exists(self.persist_directory):
            try:
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print(f"✓ 已加载现有向量数据库")
                return self.vector_store
            except Exception as e:
                print(f"✗ 加载向量数据库失败: {e}")
                return None
        return None
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """
        根据查询检索最相关的文档块
        
        Args:
            query: 查询文本
            k: 返回的相关文档数量
            
        Returns:
            相关文档列表
        """
        if self.vector_store is None:
            raise ValueError("向量数据库未初始化，请先构建或加载向量数据库")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def get_retriever(self, k: int = 3):
        """
        获取LangChain检索器
        
        Args:
            k: 返回的相关文档数量
            
        Returns:
            LangChain检索器
        """
        if self.vector_store is None:
            raise ValueError("向量数据库未初始化，请先构建或加载向量数据库")
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def get_stats(self) -> dict:
        """
        获取知识库统计信息
        
        Returns:
            包含统计信息的字典
        """
        stats = {
            "total_documents": len(self.documents),
            "total_chunks": 0,
            "vector_store_exists": self.vector_store is not None
        }
        
        if self.vector_store is not None:
            try:
                stats["total_chunks"] = self.vector_store._collection.count()
            except Exception:
                pass
        
        return stats
    
    def clear(self):
        """清空知识库和向量数据库"""
        self.documents = []
        self.vector_store = None
        
        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory)
            os.makedirs(self.persist_directory)
        print("✓ 知识库已清空")