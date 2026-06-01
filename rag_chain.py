"""
RAG问答链模块：实现提示词设计、问答链集成和对话管理
AI生成部分：系统提示词设计、ConversationalRetrievalChain集成由AI辅助生成
"""

from typing import List, Optional, Dict, Any
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory


SYSTEM_PROMPT_TEMPLATE = """你是一个专业的知识问答助手，基于提供的参考文档回答用户的问题。

请严格遵守以下规则：
1. 仅使用参考文档中提供的信息回答问题
2. 如果参考文档中没有相关信息，请明确回答"文档中未找到相关答案"
3. 回答要准确、简洁、有条理
4. 如果答案涉及多个要点，请使用分点列出
5. 不要编造或猜测文档中没有的信息

参考文档：
{context}

对话历史：
{chat_history}

现在请回答用户的问题：
{question}
"""

QA_PROMPT_TEMPLATE = """你是一个专业的知识问答助手，基于提供的参考文档回答用户的问题。

请严格遵守以下规则：
1. 仅使用参考文档中提供的信息回答问题
2. 如果参考文档中没有相关信息，请明确回答"文档中未找到相关答案"
3. 回答要准确、简洁、有条理
4. 如果答案涉及多个要点，请使用分点列出
5. 不要编造或猜测文档中没有的信息

参考文档：
{context}

用户问题：
{question}
"""

CONDENSE_QUESTION_PROMPT_TEMPLATE = """根据以下对话历史和用户的新问题，将新问题改写为一个独立的、完整的问题。

对话历史：
{chat_history}

用户新问题：
{question}

请将新问题改写为一个不需要上下文也能理解的独立问题：
"""


class RAGChain:
    """RAG问答链类，负责管理对话流程和生成答案"""
    
    def __init__(
        self,
        llm_model: str = "deepseek-r1:7b",
        temperature: float = 0.1,
        top_k: int = 3
    ):
        """
        初始化RAG问答链
        
        Args:
            llm_model: 大语言模型名称
            temperature: 生成温度，越低越确定性
            top_k: 检索返回的相关文档数量
        """
        self.llm_model = llm_model
        self.temperature = temperature
        self.top_k = top_k
        
        self.llm = ChatOllama(
            model=llm_model,
            temperature=temperature
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        self.qa_chain: Optional[ConversationalRetrievalChain] = None
        self.vector_store: Optional[Chroma] = None
    
    def set_vector_store(self, vector_store: Chroma):
        """
        设置向量数据库
        
        Args:
            vector_store: Chroma向量数据库实例
        """
        self.vector_store = vector_store
        self._build_chain()
    
    def _build_chain(self):
        """构建ConversationalRetrievalChain"""
        if self.vector_store is None:
            raise ValueError("请先设置向量数据库")
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.top_k}
        )
        
        qa_prompt = PromptTemplate(
            template=QA_PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        
        condense_prompt = PromptTemplate(
            template=CONDENSE_QUESTION_PROMPT_TEMPLATE,
            input_variables=["chat_history", "question"]
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            condense_question_prompt=condense_prompt,
            return_source_documents=True,
            verbose=False
        )
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        提问并获取答案
        
        Args:
            question: 用户问题
            
        Returns:
            包含答案、来源文档等信息的字典
        """
        if self.qa_chain is None:
            return {
                "answer": "知识库未初始化，请先上传文档并构建知识库。",
                "source_documents": [],
                "chat_history": self._get_chat_history()
            }
        
        try:
            result = self.qa_chain.invoke({"question": question})
            
            answer = result.get("answer", "").strip()
            source_docs = result.get("source_documents", [])
            
            return {
                "question": question,
                "answer": answer,
                "source_documents": source_docs,
                "chat_history": self._get_chat_history()
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"生成答案时出错: {str(e)}",
                "source_documents": [],
                "chat_history": self._get_chat_history()
            }
    
    def ask_with_simple_chain(self, question: str, vector_store: Chroma) -> Dict[str, Any]:
        """
        使用简单链提问（不使用对话记忆）
        
        Args:
            question: 用户问题
            vector_store: 向量数据库
            
        Returns:
            包含答案和来源文档的字典
        """
        retriever = vector_store.as_retriever(search_kwargs={"k": self.top_k})
        
        qa_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "你是一个专业的知识问答助手，基于提供的参考文档回答用户的问题。\n\n"
                "请严格遵守以下规则：\n"
                "1. 仅使用参考文档中提供的信息回答问题\n"
                "2. 如果参考文档中没有相关信息，请明确回答'文档中未找到相关答案'\n"
                "3. 回答要准确、简洁、有条理\n"
                "4. 不要编造或猜测文档中没有的信息\n\n"
                "参考文档：\n{context}"
            ),
            HumanMessagePromptTemplate.from_template("{question}")
        ])
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        try:
            answer = rag_chain.invoke(question)
            source_docs = retriever.invoke(question)
            
            return {
                "question": question,
                "answer": answer,
                "source_documents": source_docs
            }
        except Exception as e:
            return {
                "question": question,
                "answer": f"生成答案时出错: {str(e)}",
                "source_documents": []
            }
    
    def clear_memory(self):
        """清空对话记忆"""
        self.memory.clear()
    
    def _get_chat_history(self) -> List[Dict[str, str]]:
        """
        获取格式化的对话历史
        
        Returns:
            对话历史列表，每项包含role和content
        """
        messages = self.memory.chat_memory.messages
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
        
        return history
    
    def get_memory(self):
        """获取记忆实例，供外部使用"""
        return self.memory


def test_rag_chain():
    """测试RAG问答链"""
    from knowledge_base import KnowledgeBase
    import os
    
    print("=" * 60)
    print("RAG问答链测试")
    print("=" * 60)
    
    docs_folder = input("请输入文档文件夹路径: ").strip()
    
    if not docs_folder or not os.path.exists(docs_folder):
        print("文件夹不存在，跳过测试")
        return
    
    kb = KnowledgeBase(
        persist_directory="chroma_db_test",
        embedding_model="nomic-embed-text"
    )
    
    print("\n正在加载文档...")
    documents = kb.load_documents_from_folder(docs_folder)
    
    if not documents:
        print("未加载到文档，跳过测试")
        return
    
    print("正在构建向量数据库...")
    vector_store = kb.build_vector_store(documents)
    
    print("正在初始化RAG问答链...")
    rag = RAGChain(
        llm_model="deepseek-r1:7b",
        temperature=0.1,
        top_k=3
    )
    rag.set_vector_store(vector_store)
    
    print("\n" + "=" * 60)
    print("开始问答测试（输入exit退出）")
    print("=" * 60)
    
    while True:
        question = input("\n请输入问题: ").strip()
        
        if question.lower() in ["exit", "quit", "退出"]:
            break
        
        if not question:
            continue
        
        print("\n正在生成答案...")
        result = rag.ask(question)
        
        print("\n" + "-" * 60)
        print(f"问题: {result['question']}")
        print(f"答案: {result['answer']}")
        
        if result["source_documents"]:
            print("\n参考来源:")
            for i, doc in enumerate(result["source_documents"], 1):
                source = doc.metadata.get("source", "未知")
                content = doc.page_content[:100].replace("\n", " ")
                print(f"  [{i}] {source}: {content}...")
        print("-" * 60)
    
    # 清理测试数据
    import shutil
    if os.path.exists("chroma_db_test"):
        shutil.rmtree("chroma_db_test")


if __name__ == "__main__":
    test_rag_chain()