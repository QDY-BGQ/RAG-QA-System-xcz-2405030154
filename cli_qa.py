"""
命令行版本RAG问答脚本
AI生成部分：主流程控制和交互逻辑由AI辅助生成
"""

import os
import sys
from typing import List

from knowledge_base import KnowledgeBase
from rag_chain import RAGChain


def print_separator(char="=", length=60):
    """打印分隔线"""
    print(char * length)


def print_title(title):
    """打印标题"""
    print_separator()
    print(title.center(60))
    print_separator()


def test_qa_system():
    """测试问答系统：5个相关问题 + 2个无关问题"""
    related_questions = [
        "什么是自然语言处理？",
        "词嵌入是什么意思？",
        "Transformer模型的核心机制是什么？",
        "BERT模型的主要特点是什么？",
        "文本分类的常用方法有哪些？"
    ]
    
    unrelated_questions = [
        "珠穆朗玛峰有多高？",
        "2024年奥运会在哪里举办？"
    ]
    
    return related_questions, unrelated_questions


def main():
    print_title("RAG智能问答系统 - 命令行版本")
    
    docs_folder = input("请输入文档文件夹路径 (留空使用docs目录): ").strip()
    if not docs_folder:
        docs_folder = "docs"
    
    if not os.path.exists(docs_folder):
        print(f"✗ 文件夹不存在: {docs_folder}")
        print(f"请创建docs目录并放入至少5份PDF/DOCX文档")
        sys.exit(1)
    
    model_name = input("请输入模型名称 (默认deepseek-r1:7b): ").strip()
    if not model_name:
        model_name = "deepseek-r1:7b"
    
    print("\n正在初始化知识库...")
    kb = KnowledgeBase(
        persist_directory="chroma_db",
        embedding_model="nomic-embed-text",
        llm_model=model_name,
        chunk_size=1000,
        chunk_overlap=200
    )
    
    print("正在加载文档...")
    documents = kb.load_documents_from_folder(docs_folder)
    print(f"共加载 {len(documents)} 个文档")
    
    if not documents:
        print("✗ 未加载到任何文档，请检查文件夹内容")
        sys.exit(1)
    
    print("\n正在构建向量数据库...")
    vector_store = kb.build_vector_store(documents)
    
    print("正在初始化RAG问答链...")
    rag = RAGChain(
        llm_model=model_name,
        temperature=0.1,
        top_k=3
    )
    rag.set_vector_store(vector_store)
    
    stats = kb.get_stats()
    print(f"\n✓ 知识库初始化完成")
    print(f"  文档数量: {stats['total_documents']}")
    print(f"  文本块数量: {stats['total_chunks']}")
    
    while True:
        print("\n" + print_separator("-"))
        print("1. 手动问答")
        print("2. 运行预设测试（5个相关 + 2个无关）")
        print("3. 清空对话历史")
        print("4. 退出")
        print_separator("-")
        
        choice = input("请选择操作 (1-4): ").strip()
        
        if choice == "1":
            print_title("手动问答模式（输入exit退出）")
            while True:
                question = input("\n请输入问题: ").strip()
                if question.lower() in ["exit", "quit", "退出", "q"]:
                    break
                if not question:
                    continue
                
                print("正在生成答案...")
                result = rag.ask(question)
                
                print("\n" + "-" * 60)
                print(f"Q: {result['question']}")
                print(f"A: {result['answer']}")
                
                if result["source_documents"]:
                    print("\n[参考来源]")
                    for i, doc in enumerate(result["source_documents"], 1):
                        source = doc.metadata.get("source", "未知")
                        content = doc.page_content[:120].replace("\n", " ")
                        print(f"  {i}. {source}: {content}...")
                print("-" * 60)
        
        elif choice == "2":
            related, unrelated = test_qa_system()
            
            print_title("预设测试 - 相关问题（5个）")
            for i, question in enumerate(related, 1):
                print(f"\n[{i}/{len(related)}] 问题: {question}")
                print("正在生成答案...")
                result = rag.ask(question)
                print(f"答案: {result['answer']}")
                print("-" * 40)
            
            print_title("预设测试 - 无关问题（2个）")
            for i, question in enumerate(unrelated, 1):
                print(f"\n[{i}/{len(unrelated)}] 问题: {question}")
                print("正在生成答案...")
                result = rag.ask(question)
                print(f"答案: {result['answer']}")
                print("-" * 40)
            
            print("\n✓ 预设测试完成，请检查回答质量")
            print("  相关问题应基于文档准确回答")
            print("  无关问题应回答'文档中未找到相关答案'")
        
        elif choice == "3":
            rag.clear_memory()
            print("✓ 对话历史已清空")
        
        elif choice == "4":
            print("感谢使用，再见！")
            break
        
        else:
            print("无效选择，请输入1-4")


if __name__ == "__main__":
    main()