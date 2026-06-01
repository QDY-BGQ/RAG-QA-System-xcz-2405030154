# RAG智能问答系统

基于本地知识库的检索增强生成（RAG）智能问答系统，使用Ollama本地大模型、LangChain框架和Streamlit构建，能够"学习"指定本地文档并回答相关问题。

## 项目简介

本项目实现了一个完整的RAG智能问答系统，用户可以上传PDF或DOCX文档，系统会自动解析文档并构建本地知识库，然后基于知识库内容回答用户的问题，有效缓解大模型"幻觉"问题。

## 环境要求与安装步骤

### 环境要求
- Windows 10/11
- Python 3.10 或更高版本
- 至少8GB内存（推荐16GB以上）
- Ollama服务

### 安装步骤

#### 1. 安装Ollama
1. 访问 [Ollama官网](https://ollama.com/) 下载Windows版本安装包
2. 双击安装包完成安装
3. 打开命令行，下载模型：
```bash
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

#### 2. 创建Python虚拟环境
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. 安装依赖包
```bash
pip install -r requirements.txt
```

## 使用说明

### 运行Web应用
```bash
streamlit run app.py
```

### 功能操作
1. **文档上传**：在左侧边栏点击"上传文档"按钮，选择PDF或DOCX文件
2. **构建知识库**：上传文件后，点击"构建/更新知识库"按钮，系统将自动解析文档并构建向量库
3. **提问回答**：在主界面的输入框中输入问题，点击"提问"按钮，系统将基于知识库内容返回答案
4. **查看对话历史**：主界面会显示完整的多轮问答记录

## 关键技术点说明

### RAG流程
1. **文档加载**：支持PDF和DOCX格式文档的批量读取与文本提取
2. **文本分割**：使用RecursiveCharacterTextSplitter进行分块（chunk_size=1000，chunk_overlap=200）
3. **向量化存储**：使用Ollama的nomic-embed-text嵌入模型将文本块向量化，存入Chroma向量数据库
4. **相似性检索**：给定查询，返回最相关的3个文本块
5. **问答生成**：使用ConversationalRetrievalChain将检索器和大模型连接，生成答案

### 所用模型
- 大语言模型：deepseek-r1:7b（或qwen2:7b）
- 嵌入模型：nomic-embed-text

### 系统提示词
系统要求模型"基于提供的参考文档回答，若文档中没有相关信息则明确说'文档中未找到相关答案'"

## 项目效果截图

### 界面展示
![主界面](screenshots/main.png)
*主界面：包含对话区域和侧边栏控制面板*

![文档上传](screenshots/upload.png)
*文档上传：支持PDF和DOCX格式*

![问答示例](screenshots/qa.png)
*问答示例：基于知识库的准确回答*

## 已知问题与改进方向

- 目前仅支持PDF和DOCX格式，未来可扩展支持TXT、MD、PPT等更多格式
- 可增加知识库管理功能，支持删除特定文档
- 可增加答案引用来源显示功能
- 可优化夜间模式等UI体验

## 项目结构
```
RAG-QA-System/
├── app.py                 # Streamlit Web应用主入口
├── knowledge_base.py      # 知识库构建模块
├── rag_chain.py           # RAG问答链模块
├── cli_qa.py              # 命令行版本问答脚本
├── test_ollama.py         # Ollama环境测试脚本
├── requirements.txt       # 依赖包列表
├── .gitignore            # Git忽略文件
├── README.md             # 项目说明文档
├── docs/                 # 示例文档目录
├── chroma_db/            # 向量数据库目录（自动生成）
└── build.bat             # 打包脚本
```
