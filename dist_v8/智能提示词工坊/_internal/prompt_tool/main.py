"""
智能提示词工坊 - 入口文件
离线运行的提示词工程工具，帮助各行业用户快速生成高质量AI提示词

运行方式：
    python -m prompt_tool.main
或：
    python prompt_tool/main.py
"""

import sys
import os

# 确保包目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """主入口"""
    try:
        from .app import PromptToolApp
        app = PromptToolApp()
        app.run()
    except ImportError as e:
        # 如果相对导入失败，尝试绝对导入
        try:
            from prompt_tool.app import PromptToolApp
            app = PromptToolApp()
            app.run()
        except ImportError:
            print(f"启动失败：{e}")
            print("请确保已安装依赖：pip install customtkinter pillow")
            sys.exit(1)


if __name__ == "__main__":
    main()
