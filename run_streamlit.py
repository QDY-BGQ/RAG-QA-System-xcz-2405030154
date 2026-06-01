"""
PyInstaller运行时钩子：启动Streamlit应用
AI生成部分：PyInstaller钩子配置由AI辅助生成
"""

import os
import sys


def main():
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = 'localhost'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        app_path = os.path.join(base_path, 'app.py')
    else:
        app_path = os.path.join(os.path.dirname(__file__), 'app.py')
    
    sys.argv = [
        'streamlit',
        'run',
        app_path,
        '--server.port=8501',
        '--server.address=localhost',
        '--browser.gatherUsageStats=false'
    ]
    
    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == '__main__':
    main()