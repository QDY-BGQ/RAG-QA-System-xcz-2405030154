"""
PyInstaller打包入口脚本，用于启动Streamlit应用
"""

import os
import sys
import subprocess
import streamlit.web.cli as stcli


def main():
    """启动Streamlit应用"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    app_path = os.path.join(base_path, 'app.py')
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=false",
        "--server.port=8501"
    ]
    
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
