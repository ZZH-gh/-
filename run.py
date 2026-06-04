"""
智能提示词工坊 - 独立启动脚本
用于PyInstaller打包的入口
"""

import sys
import os
import traceback
import io

# 捕获启动错误到日志文件（windowed 模式无控制台）
_startup_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "startup_error.log")

try:
    # Chinese Windows encoding fix (PKG-03) — windowed mode has no console
    if sys.stdout is not None and sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr is not None and sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception as e:
    with open(_startup_log, "w", encoding="utf-8") as f:
        f.write(f"Encoding setup error: {e}\n{traceback.format_exc()}")

# 确保能找到包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 确保能找到包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from prompt_tool.app import PromptToolApp
        app = PromptToolApp()
        app.run()
    except Exception as e:
        error_detail = traceback.format_exc()
        # 写日志文件（windowed 模式可能无 msgbox）
        try:
            with open(_startup_log, "w", encoding="utf-8") as f:
                f.write(f"Startup error: {e}\n{error_detail}")
        except:
            pass
        # 尝试显示错误对话框
        try:
            from tkinter import messagebox
            messagebox.showerror(
                "启动失败",
                f"智能提示词工坊启动时出现错误：\n\n{str(e)}\n\n"
                f"详细信息：\n{error_detail[:500]}"
            )
        except:
            pass
        raise


if __name__ == "__main__":
    main()
