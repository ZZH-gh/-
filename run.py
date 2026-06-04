"""
智能提示词工坊 - 独立启动脚本
用于PyInstaller打包的入口
"""

import sys
import os
import traceback
import io

# 全局异常日志到 %TEMP%（桌面双击时 exe 目录可能只读）
_crash_log_path = os.path.join(
    os.environ.get("TEMP", os.path.expanduser("~")),
    "prompt_tool_crash.log"
)

def _log_crash(msg: str):
    try:
        with open(_crash_log_path, "a", encoding="utf-8") as f:
            f.write(f"{msg}\n{traceback.format_exc()}\n")
    except:
        pass

# 全局未捕获异常钩子
def _global_excepthook(etype, value, tb):
    _log_crash(f"Unhandled: {value}")
    try:
        from tkinter import messagebox
        messagebox.showerror("意外错误", f"{value}\n\n详情: {_crash_log_path}")
    except:
        pass

sys.excepthook = _global_excepthook

try:
    if sys.stdout is not None and hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr is not None and hasattr(sys.stderr, 'encoding') and sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception as e:
    _log_crash(f"Encoding: {e}")

# 确保能找到包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from prompt_tool.app import PromptToolApp
        app = PromptToolApp()
        app.run()
    except Exception as e:
        error_detail = traceback.format_exc()
        _log_crash(f"Startup: {e}")
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
