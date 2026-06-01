@echo off
chcp 65001
echo ============================================
echo RAG智能问答系统 - 打包脚本
echo ============================================
echo.

echo [1/4] 检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo 错误: 未找到虚拟环境，请先运行: python -m venv venv
    pause
    exit /b 1
)

echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/4] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo [4/4] 开始打包...
echo 这可能需要几分钟时间，请耐心等待...
echo.

pyinstaller ^
    --onefile ^
    --name RAG-QA-System ^
    --add-data "venv\Lib\site-packages\streamlit;streamlit" ^
    --hidden-import streamlit ^
    --hidden-import langchain ^
    --hidden-import langchain_community ^
    --hidden-import langchain_core ^
    --hidden-import chromadb ^
    --hidden-import pypdf ^
    --hidden-import python_docx ^
    --collect-all streamlit ^
    --collect-all langchain ^
    --collect-all langchain_community ^
    --collect-all langchain_core ^
    --collect-all chromadb ^
    --collect-all pypdf ^
    --collect-all python_docx ^
    --runtime-hook run_streamlit.py ^
    app.py

echo.
echo ============================================
echo 打包完成！
echo 可执行文件位于: dist\RAG-QA-System.exe
echo ============================================
echo.
echo 注意: 运行exe前请确保:
echo 1. Ollama服务已启动
echo 2. 已下载所需模型 (deepseek-r1:7b, nomic-embed-text)
echo.
pause