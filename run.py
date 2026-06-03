"""
智能提示词工坊 - 独立启动脚本
用于PyInstaller打包的入口
"""

import sys
import os
import traceback

# 确保能找到包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from prompt_tool.app import PromptToolApp
        app = PromptToolApp()
        app.run()
    except Exception as e:
        # 出错时显示友好信息
        from tkinter import messagebox
        error_detail = traceback.format_exc()
        messagebox.showerror(
            "启动失败",
            f"智能提示词工坊启动时出现错误：\n\n{str(e)}\n\n"
            f"详细信息：\n{error_detail[:500]}"
        )
        raise


if __name__ == "__main__":
    main()
