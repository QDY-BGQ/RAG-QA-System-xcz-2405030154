from knowledge_base import KnowledgeBase
import os
import glob

kb = KnowledgeBase(
    persist_directory='chroma_db',
    embedding_model='nomic-embed-text',
    llm_model='deepseek-r1:7b',
    chunk_size=1000,
    chunk_overlap=200
)

docs_dir = 'docs'
docx_files = glob.glob(os.path.join(docs_dir, '*.docx'))
pdf_files = glob.glob(os.path.join(docs_dir, '*.pdf'))
txt_files = glob.glob(os.path.join(docs_dir, '*.txt'))
all_files = docx_files + pdf_files + txt_files

print(f'找到 {len(all_files)} 个文件')
print(f'  - DOCX: {len(docx_files)} 个')
print(f'  - PDF: {len(pdf_files)} 个')
print(f'  - TXT: {len(txt_files)} 个')

all_documents = []
for file_path in all_files:
    print(f'正在加载: {os.path.basename(file_path)}')
    try:
        docs = kb.load_single_document(file_path)
        all_documents.extend(docs)
        print(f'  加载成功，{len(docs)} 个文档')
    except Exception as e:
        print(f'  加载失败: {e}')
        import traceback
        traceback.print_exc()

print(f'\n总共加载了 {len(all_documents)} 个文档')

if all_documents:
    print('\n正在构建向量数据库...')
    print('这可能需要一些时间，取决于Ollama模型加载速度...')
    try:
        vector_store = kb.build_vector_store(all_documents)
        print('向量数据库构建成功！')
        stats = kb.get_stats()
        doc_count = stats.get("total_documents", 0)
        chunk_count = stats.get("total_chunks", 0)
        print(f'文档数: {doc_count}')
        print(f'文本块数: {chunk_count}')
        print('\n知识库已准备就绪！')
    except Exception as e:
        print(f'构建失败: {e}')
        import traceback
        traceback.print_exc()