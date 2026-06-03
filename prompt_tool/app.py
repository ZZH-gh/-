"""
智能提示词工坊 - UI主界面
核心流程：简短输入 → 3个可直接扔给AI执行的提示词
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import threading
import time
import os

from .engine import AnalysisEngine
from .generator import generate_prompts
from .knowledge import (
    STRATEGIES, get_all_industry_names
)
from .knowledge_manager import knowledge_manager
from .session_manager import session_manager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class PromptToolApp:

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🧠 智能提示词工坊 v3.0")
        self.root.geometry("1050x740")
        self.root.minsize(850, 580)

        self.analysis_result = None
        self.generated_prompts = None
        self.current_strategy = "direct"

        # Phase 2: Initialize knowledge manager (before AnalysisEngine)
        knowledge_manager.initialize()
        # Phase 3: Initialize session manager (placeholder — Phase 4 adds session creation)
        session_manager.initialize()

        self.engine = AnalysisEngine()

        self.colors = {
            "primary": "#2B579A", "secondary": "#4A90D9",
            "accent": "#E67E22", "success": "#27AE60",
            "text": "#2C3E50", "text_light": "#7F8C8D",
            "card": "#FFFFFF", "body": "#F0F2F5", "border": "#DEE2E6",
        }

        self._setup_ui()
        self._center_window()

        # Check fallback status after UI is built so set_status works
        if knowledge_manager.is_fallback_active():
            self.set_status("⚠️ 知识包加载失败，使用 v3.0 兼容模式")

    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ================================================================
    # UI 构建
    # ================================================================

    def _setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=0)  # 标题
        self.root.grid_rowconfigure(1, weight=0)  # 输入区
        self.root.grid_rowconfigure(2, weight=0)  # 分析信息条
        self.root.grid_rowconfigure(3, weight=1)  # 三大方案
        self.root.grid_rowconfigure(4, weight=0)  # 状态栏

        self._build_header()
        self._build_input_area()
        self._build_info_bar()
        self._build_strategies_area()
        self._build_status_bar()

    def _build_header(self):
        h = ctk.CTkFrame(self.root, height=60, corner_radius=0,
                         fg_color=self.colors["primary"])
        h.grid(row=0, column=0, sticky="nsew")
        h.grid_propagate(False)
        h.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(h, text="🧠  智能提示词工坊",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="white").grid(row=0, column=0, padx=25, pady=(6, 0), sticky="w")

        ctk.CTkLabel(h, text="说出你的需求 → 一键生成可直接让 AI 执行的提示词",
                     font=ctk.CTkFont(size=12),
                     text_color="white").grid(row=1, column=0, padx=25, pady=(0, 6), sticky="w")

        ctk.CTkLabel(h, text="v3.0", font=ctk.CTkFont(size=11),
                     text_color="white").grid(row=0, column=1, padx=15, rowspan=2, sticky="e")

    def _build_input_area(self):
        f = ctk.CTkFrame(self.root, corner_radius=8, fg_color=self.colors["card"])
        f.grid(row=1, column=0, padx=12, pady=(8, 3), sticky="nsew")
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(f, text="📝 描述你的需求",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["text"]
                     ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.char_label = ctk.CTkLabel(f, text="0 字", font=ctk.CTkFont(size=11),
                                       text_color=self.colors["text_light"])
        self.char_label.grid(row=0, column=2, padx=12, pady=(8, 2), sticky="e")

        self.input_text = ctk.CTkTextbox(
            f, height=70, font=ctk.CTkFont(size=13),
            wrap="word", fg_color="white", text_color=self.colors["text"],
            border_width=1, border_color=self.colors["border"], corner_radius=6,
        )
        self.input_text.grid(row=1, column=0, columnspan=3, padx=12, pady=(2, 6), sticky="nsew")
        self.input_text.insert("1.0", "例如：帮我做一个项目进度管理表，含任务名、负责人、起止日期、进度状态")
        self._ph_active = True
        self.input_text.bind("<FocusIn>", lambda _: self._on_focus_in())
        self.input_text.bind("<FocusOut>", lambda _: self._on_focus_out())
        self.input_text.bind("<KeyRelease>", self._on_input_change)

        bar = ctk.CTkFrame(f, fg_color="transparent", height=36)
        bar.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="ew")
        bar.grid_columnconfigure(2, weight=1)
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text="行业：", font=ctk.CTkFont(size=12),
                     text_color=self.colors["text"]).grid(row=0, column=0, padx=(0, 4))

        self.industry_combo = ctk.CTkComboBox(
            bar, values=["自动识别"] + get_all_industry_names(),
            width=180, font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12), state="readonly",
        )
        self.industry_combo.set("自动识别")
        self.industry_combo.grid(row=0, column=1, padx=(0, 10))

        self.gen_btn = ctk.CTkButton(
            bar, text="🎯  生成提示词", font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["primary"], hover_color="#1A3F6D",
            height=32, width=130, command=self._on_generate,
        )
        self.gen_btn.grid(row=0, column=3, padx=(0, 5), sticky="e")

        ctk.CTkButton(bar, text="清空", font=ctk.CTkFont(size=11),
                      fg_color="#E74C3C", hover_color="#C0392B",
                      height=28, width=65, command=self._on_clear
                      ).grid(row=0, column=4)

    def _build_info_bar(self):
        """分析信息条"""
        self.info_bar = ctk.CTkFrame(self.root, fg_color="#F0F4F8",
                                     corner_radius=6, height=30)
        self.info_bar.grid(row=2, column=0, padx=12, pady=3, sticky="ew")
        self.info_bar.grid_propagate(False)
        self.info_bar.grid_columnconfigure(3, weight=1)

        self.industry_info = ctk.CTkLabel(self.info_bar, text="🏢 行业：等待输入",
                                          font=ctk.CTkFont(size=12),
                                          text_color=self.colors["text_light"])
        self.industry_info.grid(row=0, column=0, padx=(10, 12), sticky="w")

        self.task_info = ctk.CTkLabel(self.info_bar, text="📌 任务：—",
                                      font=ctk.CTkFont(size=12),
                                      text_color=self.colors["text_light"])
        self.task_info.grid(row=0, column=1, padx=(0, 12), sticky="w")

    def _build_strategies_area(self):
        """三大方案区域：3个策略标签 + 1个展示区"""
        f = ctk.CTkFrame(self.root, corner_radius=8, fg_color=self.colors["card"])
        f.grid(row=3, column=0, padx=12, pady=3, sticky="nsew")
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(2, weight=1)

        # 策略标签
        tab_h = ctk.CTkFrame(f, fg_color="transparent", height=42)
        tab_h.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        tab_h.grid_columnconfigure((0, 1, 2), weight=1)

        self.strategy_btns = {}
        strategies = [
            ("direct",  "⚡ 高效直给式", "推荐", self.colors["secondary"]),
            ("roleplay","🎭 角色委派式", "专业", "#E67E22"),
            ("detailed","📋 完整详细式", "全面", self.colors["success"]),
        ]
        for i, (key, name, tag, color) in enumerate(strategies):
            c = ctk.CTkFrame(tab_h, fg_color="transparent")
            c.grid(row=0, column=i, padx=4, sticky="ew")
            c.grid_columnconfigure(0, weight=1)

            btn = ctk.CTkButton(c, text=f"{name}",
                                font=ctk.CTkFont(size=13, weight="bold"),
                                fg_color=color, hover_color=self._darken(color),
                                height=36, corner_radius=6,
                                command=lambda k=key: self._switch_strategy(k))
            btn.grid(row=0, column=0, sticky="ew")
            self.strategy_btns[key] = btn

        # 操作栏
        act = ctk.CTkFrame(f, fg_color="transparent", height=32)
        act.grid(row=1, column=0, padx=12, pady=(6, 0), sticky="ew")
        act.grid_columnconfigure(0, weight=1)
        act.grid_propagate(False)

        self.prompt_title = ctk.CTkLabel(act, text="✨ 提示词",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         text_color=self.colors["text"])
        self.prompt_title.grid(row=0, column=0, sticky="w")

        self.copy_btn = ctk.CTkButton(
            act, text="📋 复制此提示词", font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=self.colors["success"], hover_color="#1E8449",
            height=28, width=130, state="disabled", command=self._on_copy,
        )
        self.copy_btn.grid(row=0, column=1, padx=(0, 5), sticky="e")

        self.export_btn = ctk.CTkButton(
            act, text="💾 导出全部 3 个", font=ctk.CTkFont(size=11),
            fg_color=self.colors["secondary"], hover_color="#357ABD",
            height=28, width=130, state="disabled", command=self._on_export,
        )
        self.export_btn.grid(row=0, column=2, sticky="e")

        # 提示词展示框
        df = ctk.CTkFrame(f, fg_color="white", corner_radius=6,
                          border_width=1, border_color=self.colors["border"])
        df.grid(row=2, column=0, padx=12, pady=(6, 12), sticky="nsew")
        df.grid_columnconfigure(0, weight=1)
        df.grid_rowconfigure(0, weight=1)

        self.display = ctk.CTkTextbox(
            df, font=ctk.CTkFont(size=13, family="Microsoft YaHei"),
            wrap="word", fg_color="white", text_color=self.colors["text"],
            border_width=0, corner_radius=4,
        )
        self.display.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self._set_placeholder()

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self.root, height=26, corner_radius=0, fg_color="#E8ECF0")
        bar.grid(row=4, column=0, sticky="nsew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(bar, text="💡 输入需求 → 点击「生成提示词」",
                                   font=ctk.CTkFont(size=11),
                                   text_color=self.colors["text_light"])
        self.status.grid(row=0, column=0, padx=15, sticky="w")

    # ================================================================
    # 核心逻辑
    # ================================================================

    def _on_generate(self):
        content = self.input_text.get("1.0", "end-1c").strip()
        if not content or self._ph_active:
            messagebox.showwarning("提示", "请先输入你的需求描述")
            return

        self.gen_btn.configure(state="disabled", text="⏳ 生成中...")
        self.set_status("🔍 正在分析需求并生成提示词...")

        thread = threading.Thread(target=self._do_generate, args=(content,), daemon=True)
        thread.start()

    def _do_generate(self, content):
        try:
            manual = self.industry_combo.get()
            if manual == "自动识别":
                manual = None
            time.sleep(0.15)

            self.analysis_result = self.engine.analyze(content, manual)
            self.generated_prompts = generate_prompts(self.analysis_result)
            self.root.after(0, self._on_done)
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _on_done(self):
        r = self.analysis_result
        self.industry_info.configure(text=f"🏢 {r['industry_name']}")
        self.task_info.configure(text=f"📌 {r['task_name']}")

        self._show_prompt()
        self.gen_btn.configure(state="normal", text="🎯  生成提示词")
        self.copy_btn.configure(state="normal")
        self.export_btn.configure(state="normal")

        self.set_status(f"✅ 已生成 3 个提示词方案（{r['industry_name']}·{r['task_name']}）")

    def _on_error(self, msg):
        self.gen_btn.configure(state="normal", text="🎯  生成提示词")
        self.set_status(f"❌ 出错：{msg}")
        messagebox.showerror("错误", f"生成出错：\n{msg}")

    def _switch_strategy(self, key):
        self.current_strategy = key
        self._show_prompt()

    def _show_prompt(self):
        if not self.generated_prompts:
            return

        prompt = self.generated_prompts.get(self.current_strategy, "")
        if not prompt:
            prompt = "暂未生成此方案。"

        self.display.configure(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0", prompt)
        self.display.configure(state="disabled")

        sn = STRATEGIES[self.current_strategy]["name"]
        self.prompt_title.configure(text=f"✨ {sn}")

        for key, btn in self.strategy_btns.items():
            colors = {"direct": self.colors["secondary"],
                      "roleplay": "#E67E22",
                      "detailed": self.colors["success"]}
            if key == self.current_strategy:
                btn.configure(fg_color=self._darken(colors.get(key, "#4A90D9")))
            else:
                btn.configure(fg_color=colors.get(key, "#4A90D9"))

        self.set_status(f"✅ 当前：{sn}")

    # ================================================================
    # 复制 / 导出
    # ================================================================

    def _on_copy(self):
        if not self.generated_prompts:
            return
        prompt = self.generated_prompts.get(self.current_strategy, "")
        if not prompt:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)

        sn = STRATEGIES[self.current_strategy]["name"]
        self.set_status(f"✅ 已复制：{sn}")
        self.copy_btn.configure(text="✅ 已复制", fg_color=self.colors["secondary"])
        self.root.after(2000, lambda: self.copy_btn.configure(
            text="📋 复制此提示词", fg_color=self.colors["success"]))

    def _on_export(self):
        if not self.generated_prompts:
            return

        lines = [
            "=" * 60,
            "🧠 智能提示词工坊 - 3个可直接执行的提示词",
            f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"需求：{self.analysis_result.get('original_input', '')}",
            f"行业：{self.analysis_result.get('industry_name', '')}",
            f"任务：{self.analysis_result.get('task_name', '')}",
            "=" * 60,
            "",
            "【使用方法】复制下方任一提示词，直接发给 ChatGPT/Claude/文心一言 等 AI 即可执行。",
            "",
        ]
        for sk in ["direct", "roleplay", "detailed"]:
            p = self.generated_prompts.get(sk, "")
            if p:
                sn = STRATEGIES[sk]["name"]
                lines.extend([f"{'='*50}", f"方案：{sn}", f"{'='*50}", "", p, ""])

        text = "\n".join(lines)

        self.root.clipboard_clear()
        self.root.clipboard_append(text)

        try:
            path = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(path):
                path = os.path.expanduser("~")
            fp = os.path.join(path, f"提示词方案_{time.strftime('%Y%m%d_%H%M%S')}.txt")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(text)
            self.set_status("✅ 已导出到桌面（已同时复制到剪贴板）")
            messagebox.showinfo("导出成功", f"3 个提示词方案已导出到：\n{fp}")
        except Exception:
            self.set_status("✅ 已复制到剪贴板")
            messagebox.showinfo("导出成功", "已复制到剪贴板，请粘贴保存。")

    # ================================================================
    # 输入事件
    # ================================================================

    def _on_focus_in(self):
        if self._ph_active:
            self.input_text.delete("1.0", "end")
            self._ph_active = False

    def _on_focus_out(self):
        if not self.input_text.get("1.0", "end-1c").strip():
            self.input_text.insert("1.0", "例如：帮我做一个项目进度管理表，含任务名、负责人、起止日期、进度状态")
            self._ph_active = True

    def _on_input_change(self, _=None):
        n = len(self.input_text.get("1.0", "end-1c").replace(" ", "").replace("\n", ""))
        self.char_label.configure(text=f"{n} 字")

    def _on_clear(self):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "例如：帮我做一个项目进度管理表，含任务名、负责人、起止日期、进度状态")
        self._ph_active = True
        self.analysis_result = None
        self.generated_prompts = None
        self.industry_info.configure(text="🏢 行业：等待输入")
        self.task_info.configure(text="📌 任务：—")
        self._set_placeholder()
        self.copy_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.gen_btn.configure(state="normal", text="🎯  生成提示词")
        self.set_status("💡 输入需求 → 点击「生成提示词」")

    # ================================================================
    # 工具
    # ================================================================

    def _set_placeholder(self):
        self.display.configure(state="normal")
        self.display.delete("1.0", "end")
        self.display.insert("1.0",
            "📝 在上方输入你的需求，点击「生成提示词」\n\n"
            "例如输入：\n"
            "  · 帮我做一个项目进度管理表\n"
            "  · 写一份产品需求文档，电商小程序\n"
            "  · 帮我分析销售数据，找出问题和改进方向\n"
            "  · 设计初中数学勾股定理教案\n"
            "  · 写一篇新品推广的公众号推文\n\n"
            "系统会自动识别行业和任务，生成3个可直接复制、\n"
            "直接发给 AI 执行的专业提示词！"
        )
        self.display.configure(state="disabled")
        self.prompt_title.configure(text="✨ 提示词")

    def set_status(self, msg):
        self.status.configure(text=msg)

    def _darken(self, c, a=0.2):
        c = c.lstrip("#")
        r, g, b = int(c[:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        return f"#{int(r*(1-a)):02x}{int(g*(1-a)):02x}{int(b*(1-a)):02x}"

    def run(self):
        self.root.mainloop()
