@echo off
chcp 65001
echo ========================================
echo  RAG智能问答系统 - 打包脚本
echo ========================================
echo.
echo [1/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist RAG-QA-System.spec del /q RAG-QA-System.spec
echo ✓ 清理完成
echo.
echo [2/4] 检查依赖...
python -c "import streamlit; import langchain; import chromadb; print('✓ 依赖检查通过')"
if errorlevel 1 (
    echo ✗ 依赖检查失败，请先安装所有依赖包
    echo 执行: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.
echo [3/4] 开始打包...
pyinstaller ^
    --onefile ^
    --name RAG-QA-System ^
    --icon NONE ^
    --add-data "chroma_db;chroma_db" ^
    --add-data "docs;docs" ^
    --collect-all streamlit ^
    --collect-all langchain ^
    --collect-all chromadb ^
    --collect-all langchain_community ^
    --collect-all langchain_core ^
    run_streamlit.py
if errorlevel 1 (
    echo ✗ 打包失败
    pause
    exit /b 1
)
echo.
echo [4/4] 复制必要文件到dist目录...
copy requirements.txt dist\
copy README.md dist\
if exist docs xcopy /e /i docs dist\docs\
echo ✓ 打包完成！
echo.
echo ========================================
echo  可执行文件位置: dist\RAG-QA-System.exe
echo ========================================
echo.
echo 注意事项:
echo 1. 运行前请确保Ollama服务已启动
 echo 2. 确保已下载模型: deepseek-r1:7b 和 nomic-embed-text
 echo 3. 首次运行会自动解压依赖文件，请耐心等待
 pause
