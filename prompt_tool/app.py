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
from .conversation_engine import ConversationEngine, ConversationState
from .app_controller import AppController

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

        # Phase 6: V4 scaffolding (chat_frame + result_frame + page switching)
        self._setup_v4_scaffolding()
        self._build_v4_chat_page()
        self._build_v4_result_page()
        self._init_v4_controller()

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
        self.root.grid_rowconfigure(4, weight=0)  # （保留——v3 策略区域底边）
        self.root.grid_rowconfigure(5, weight=0)  # 状态栏（v3/v4 共用）

        self._build_header()
        self._build_input_area()
        self._build_info_bar()
        self._build_strategies_area()
        self._build_status_bar()

    def _build_header(self):
        self._v3_header = ctk.CTkFrame(self.root, height=60, corner_radius=0,
                                        fg_color=self.colors["primary"])
        self._v3_header.grid(row=0, column=0, sticky="nsew")
        self._v3_header.grid_propagate(False)
        self._v3_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self._v3_header, text="🧠  智能提示词工坊",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="white").grid(row=0, column=0, padx=25, pady=(6, 0), sticky="w")

        ctk.CTkLabel(self._v3_header, text="说出你的需求 → 一键生成可直接让 AI 执行的提示词",
                     font=ctk.CTkFont(size=12),
                     text_color="white").grid(row=1, column=0, padx=25, pady=(0, 6), sticky="w")

        ctk.CTkLabel(self._v3_header, text="v3.0", font=ctk.CTkFont(size=11),
                     text_color="white").grid(row=0, column=1, padx=15, rowspan=2, sticky="e")

    def _build_input_area(self):
        self._v3_input_area = ctk.CTkFrame(self.root, corner_radius=8, fg_color=self.colors["card"])
        self._v3_input_area.grid(row=1, column=0, padx=12, pady=(8, 3), sticky="nsew")
        self._v3_input_area.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self._v3_input_area, text="📝 描述你的需求",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=self.colors["text"]
                     ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.char_label = ctk.CTkLabel(self._v3_input_area, text="0 字", font=ctk.CTkFont(size=11),
                                       text_color=self.colors["text_light"])
        self.char_label.grid(row=0, column=2, padx=12, pady=(8, 2), sticky="e")

        self.input_text = ctk.CTkTextbox(
            self._v3_input_area, height=70, font=ctk.CTkFont(size=13),
            wrap="word", fg_color="white", text_color=self.colors["text"],
            border_width=1, border_color=self.colors["border"], corner_radius=6,
        )
        self.input_text.grid(row=1, column=0, columnspan=3, padx=12, pady=(2, 6), sticky="nsew")
        self.input_text.insert("1.0", "例如：帮我做一个项目进度管理表，含任务名、负责人、起止日期、进度状态")
        self._ph_active = True
        self.input_text.bind("<FocusIn>", lambda _: self._on_focus_in())
        self.input_text.bind("<FocusOut>", lambda _: self._on_focus_out())
        self.input_text.bind("<KeyRelease>", self._on_input_change)

        bar = ctk.CTkFrame(self._v3_input_area, fg_color="transparent", height=36)
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

        # Phase 6: Knowledge pack visibility button (UI-04)
        self.kb_btn = ctk.CTkButton(self.info_bar, text="📚 知识包",
                                     width=85, height=22,
                                     font=ctk.CTkFont(size=11),
                                     fg_color="transparent",
                                     text_color=self.colors["primary"],
                                     border_color=self.colors["border"],
                                     border_width=1,
                                     command=self._on_show_knowledge_pack)
        self.kb_btn.grid(row=0, column=2, padx=(0, 10), sticky="e")

    def _build_strategies_area(self):
        """三大方案区域：3个策略标签 + 1个展示区"""
        self._v3_strategies_area = ctk.CTkFrame(self.root, corner_radius=8, fg_color=self.colors["card"])
        self._v3_strategies_area.grid(row=3, column=0, padx=12, pady=3, sticky="nsew")
        self._v3_strategies_area.grid_columnconfigure(0, weight=1)
        self._v3_strategies_area.grid_rowconfigure(2, weight=1)

        # 策略标签
        tab_h = ctk.CTkFrame(self._v3_strategies_area, fg_color="transparent", height=42)
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
        act = ctk.CTkFrame(self._v3_strategies_area, fg_color="transparent", height=32)
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
        df = ctk.CTkFrame(self._v3_strategies_area, fg_color="white", corner_radius=6,
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
        self._v3_status_bar = ctk.CTkFrame(self.root, height=26, corner_radius=0, fg_color="#E8ECF0")
        self._v3_status_bar.grid(row=5, column=0, sticky="nsew")
        self._v3_status_bar.grid_propagate(False)
        self._v3_status_bar.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(self._v3_status_bar, text="💡 输入需求 → 点击「生成提示词」",
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

        # Phase 4: Use conversation engine for multi-turn flow
        thread = threading.Thread(target=self._do_generate_v4, args=(content,), daemon=True)
        thread.start()

    def _do_generate_v4(self, content):
        """v4.0 conversation flow: analyze → auto-confirm → generate directly."""
        try:
            engine = ConversationEngine()

            # Step 1: Analyze
            result = engine.start(content)

            if result.get("needs_clarification"):
                # Low confidence — use v3.0 fallback for speed
                manual = self.industry_combo.get()
                if manual == "自动识别":
                    manual = None
                self.analysis_result = self.engine.analyze(content, manual)
                self.generated_prompts = generate_prompts(self.analysis_result)
                self.root.after(0, lambda: self._show_generate_result(engine, result))
                return

            # Step 2: Auto-confirm → skip follow-up → generate directly
            engine.handle_confirmation(True)
            self._engine = engine

            # generate_complete() now internally builds context + calls PromptGeneratorV2 (D-03)
            gen_result = engine.generate_complete()

            self.analysis_result = engine._last_analysis
            self.generated_prompts = gen_result.get("prompts", {})
            self.root.after(0, self._on_done)
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _show_generate_result(self, engine, result):
        """Show generation result with clarification note."""
        self.set_status(f"🤔 {result.get('message', '信息不够详细，已用通用模式生成')}")
        self._on_done()

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

    # Phase 6: Knowledge pack visibility (UI-04)
    def _on_show_knowledge_pack(self):
        """显示当前行业知识包概览。"""
        msg = "当前行业知识包概览\n\n"
        index = knowledge_manager.get_index()
        if not index:
            msg += "（无可用知识包，使用 v3.0 兼容模式）"
        else:
            for kid, entry in index.items():
                msg += f"🏢 {entry.get('name', kid)}\n"
                stats = entry.get('stats', {})
                msg += f"  术语: {stats.get('term_count', '?')}  场景: {stats.get('scenario_count', '?')}\n"
                msg += f"  追问树: {stats.get('tree_count', '?')}  角色: {stats.get('role_count', '?')}\n"
                msg += f"  简介: {entry.get('description', '暂无')}\n\n"
        messagebox.showinfo("知识包概览", msg)

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

    # ================================================================
    # Phase 6: V4 Frame Scaffolding (Task 1)
    # ================================================================

    def _setup_v4_scaffolding(self):
        """创建 v4 容器帧（chat_frame + result_frame），默认隐藏"""
        self.v4_container = ctk.CTkFrame(self.root, fg_color=self.colors["body"])
        self.v4_container.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.v4_container.grid_remove()  # 默认隐藏，v3 优先显示
        self.v4_container.grid_columnconfigure(0, weight=1)
        self.v4_container.grid_rowconfigure(0, weight=1)

        # Chat frame（对话界面）
        self.chat_frame = ctk.CTkFrame(self.v4_container, fg_color=self.colors["body"])
        self.chat_frame.grid(row=0, column=0, sticky="nsew")
        self.chat_frame.grid_remove()  # 初始隐藏
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=0)  # header
        self.chat_frame.grid_rowconfigure(1, weight=1)  # chat scrollable area
        self.chat_frame.grid_rowconfigure(2, weight=0)  # input bar

        # Result frame（结果界面）
        self.result_frame = ctk.CTkFrame(self.v4_container, fg_color=self.colors["body"])
        self.result_frame.grid(row=0, column=0, sticky="nsew")
        self.result_frame.grid_remove()  # 初始隐藏
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(1, weight=1)

    def _switch_to_v4_page(self, page_name: str):
        """切换到 v4 的指定子页面

        Args:
            page_name: "chat" 或 "results"
        """
        # 隐藏 v3 所有直接子控件（状态栏除外——跨页面持久化）
        self._v3_header.grid_remove()
        self._v3_input_area.grid_remove()
        self.info_bar.grid_remove()
        self._v3_strategies_area.grid_remove()

        # 显示 v4 容器
        self.v4_container.grid()

        # 在 chat_frame 和 result_frame 间切换
        if page_name == "chat":
            self.result_frame.grid_remove()
            self.chat_frame.grid()
        elif page_name == "results":
            self.chat_frame.grid_remove()
            self.result_frame.grid()

    def _switch_to_v3(self):
        """切回 v3 视图

        状态栏保持在 row=5 不变，无需重新 grid。
        """
        self.v4_container.grid_remove()

        # 恢复 v3 控件（状态栏从未隐藏，无需恢复）
        self._v3_header.grid(row=0, column=0, sticky="nsew")
        self._v3_input_area.grid(row=1, column=0, padx=12, pady=(8, 3), sticky="nsew")
        self.info_bar.grid(row=2, column=0, padx=12, pady=3, sticky="ew")
        self._v3_strategies_area.grid(row=3, column=0, padx=12, pady=3, sticky="nsew")

    # ================================================================
    # Phase 6: V4 Chat Page — 气泡流 + 输入栏 + 逃生门 (Task 2)
    # ================================================================

    def _build_v4_chat_page(self):
        """构建对话页面：header + 滚动气泡区域 + 底部输入栏"""
        # --- Header (row 0) ---
        h = ctk.CTkFrame(self.chat_frame, height=60, corner_radius=0,
                         fg_color=self.colors["primary"])
        h.grid(row=0, column=0, sticky="nsew")
        h.grid_propagate(False)
        h.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(h, text="🧠 智能提示词工坊 v4.0",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").grid(row=0, column=0, padx=20, sticky="w")

        # Knowledge pack button (placeholder — enabled in Plan 06-03)
        self._v4_kb_btn = ctk.CTkButton(
            h, text="📚 知识包", width=80, height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", text_color="white",
            border_color="white", border_width=1,
            state="disabled",
        )
        self._v4_kb_btn.grid(row=0, column=1, padx=15, sticky="e")

        # --- Chat scrollable area (row 1) ---
        self.chat_scrollable = ctk.CTkScrollableFrame(
            self.chat_frame, fg_color=self.colors["body"]
        )
        self.chat_scrollable.grid(row=1, column=0, sticky="nsew")
        self.chat_scrollable.grid_columnconfigure(0, weight=1)

        self._chat_row_count = 0
        self._messages = []

        self._add_welcome_message()

        # --- Input bar (row 2) ---
        self._build_v4_input_bar()

    def _build_v4_input_bar(self):
        """底部输入栏：文本输入框 + 发送按钮 + 逃生门"""
        bar = ctk.CTkFrame(self.chat_frame, fg_color=self.colors["card"],
                           height=60, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        # Input textbox
        self.v4_input = ctk.CTkTextbox(
            bar, height=36, font=ctk.CTkFont(size=13),
            wrap="word", fg_color="white",
            border_width=1, border_color=self.colors["border"],
            corner_radius=6,
        )
        self.v4_input.grid(row=0, column=0, padx=(12, 4), pady=10, sticky="ew")

        # Send button
        self.send_btn = ctk.CTkButton(
            bar, text="▶", width=36, height=36,
            fg_color=self.colors["primary"],
            command=self._on_v4_send,
        )
        self.send_btn.grid(row=0, column=1, padx=2, pady=10)

        # Escape door (D-09): 🎯 立即生成
        self.escape_btn = ctk.CTkButton(
            bar, text="🎯 立即生成", height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#E67E22", hover_color="#D35400",
            command=self._on_v4_escape,
        )
        self.escape_btn.grid(row=0, column=2, padx=(4, 12), pady=10)

    # ================================================================
    # AppController 集成
    # ================================================================

    def _init_v4_controller(self):
        """创建 AppController，用 root.after 包装回调确保线程安全"""
        self._v4_controller = AppController(
            on_state_change=lambda d: self.root.after(
                0, lambda: self._v4_on_state_change(d)),
            on_question=lambda d: self.root.after(
                0, lambda: self._v4_on_question(d)),
            on_results=lambda d: self.root.after(
                0, lambda: self._v4_on_results(d)),
            on_error=lambda d: self.root.after(
                0, lambda: self._v4_on_error(d)),
        )
        self._v4_is_generating = False
        self._active_options_frame: ctk.CTkFrame | None = None
        self._multi_choice_vars: dict[str, tk.BooleanVar] = {}

    # ================================================================
    # 消息气泡渲染
    # ================================================================

    def _add_user_message(self, text: str):
        """用户消息气泡：右对齐 (sticky=e)，浅蓝底 (D-06)"""
        bubble = ctk.CTkFrame(
            self.chat_scrollable,
            fg_color="#D4E6F1",
            corner_radius=10,
        )
        msg = ctk.CTkLabel(
            bubble, text=text,
            wraplength=350,
            justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#2C3E50",
        )
        msg.pack(padx=12, pady=8)

        bubble.grid(row=self._chat_row_count, column=0,
                    sticky="e", padx=(60, 10), pady=4)
        self._chat_row_count += 1
        self._messages.append({"role": "user", "content": text, "msg_type": "text"})
        self.root.after(50, self._scroll_chat_to_bottom)

    def _add_system_message(self, text: str):
        """系统消息气泡：左对齐 (sticky=w)，白底 (D-06)"""
        bubble = ctk.CTkFrame(
            self.chat_scrollable,
            fg_color="#FFFFFF",
            corner_radius=10,
        )
        msg = ctk.CTkLabel(
            bubble, text=text,
            wraplength=450,
            justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#2C3E50",
        )
        msg.pack(padx=12, pady=8)

        bubble.grid(row=self._chat_row_count, column=0,
                    sticky="w", padx=(10, 60), pady=4)
        self._chat_row_count += 1
        self._messages.append({"role": "system", "content": text, "msg_type": "text"})
        self.root.after(50, self._scroll_chat_to_bottom)

    def _add_welcome_message(self):
        """显示初始欢迎消息"""
        welcome = (
            "欢迎使用智能提示词工坊 v4.0\n\n"
            "输入您的需求，我会引导您一步步完善提示词，"
            "帮您生成可直接扔给 AI 执行的专业提示词。\n\n"
            "💡 提示：描述越具体，效果越好！"
        )
        self._add_system_message(welcome)

    def _scroll_chat_to_bottom(self):
        """自动滚动到对话底部

        增强版：先完成布局计算再滚动，捕获异常做降级处理。
        但不要递归重试（RESEARCH.md Pitfall 1 — 静默降级即可）。
        """
        try:
            self.chat_scrollable.update_idletasks()
            self.chat_scrollable._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # ================================================================
    # 交互控件（single_choice / multi_choice / confirm）
    # ================================================================

    def _cleanup_options_frame(self):
        """销毁当前选项 frame 并重置状态"""
        if self._active_options_frame is not None:
            try:
                self._active_options_frame.destroy()
            except Exception:
                pass
            self._active_options_frame = None
        self._multi_choice_vars = {}

    def _add_single_choice_options(self, options: list):
        """单选按钮组：每个选项一个可点击按钮 (D-08)"""
        self._cleanup_options_frame()

        choice_frame = ctk.CTkFrame(
            self.chat_scrollable,
            fg_color="transparent",
        )

        for i, opt in enumerate(options):
            label = opt.get("label", opt.get("value", "选项"))
            btn = ctk.CTkButton(
                choice_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                fg_color="#F0F4F8",
                text_color=self.colors["text"],
                hover_color="#D4E6F1",
                border_width=1,
                border_color=self.colors["border"],
                height=30,
                corner_radius=6,
                command=lambda v=opt.get("value"): self._on_option_selected(v),
            )
            btn.grid(row=0, column=i, padx=4, pady=(0, 8), sticky="w")

        choice_frame.grid(row=self._chat_row_count, column=0,
                          sticky="w", padx=(10, 60), pady=(0, 4))
        self._chat_row_count += 1
        self._active_options_frame = choice_frame

    def _on_option_selected(self, value: str):
        """单选按钮点击：提交选项值"""
        self._add_user_message(f"选择：{value}")
        self._cleanup_options_frame()

        self.send_btn.configure(state="disabled", text="⏳")
        self._v4_is_generating = True
        self._v4_controller.process_answer(value)

    def _add_multi_choice_options(self, options: list):
        """多选复选框组：每个选项一个复选框 + 确认按钮 (D-08)"""
        self._cleanup_options_frame()

        choice_frame = ctk.CTkFrame(
            self.chat_scrollable,
            fg_color="transparent",
        )

        self._multi_choice_vars = {}
        for i, opt in enumerate(options):
            label = opt.get("label", opt.get("value", "选项"))
            var = tk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                choice_frame,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text"],
            )
            cb.grid(row=i, column=0, padx=(0, 8), pady=2, sticky="w")
            self._multi_choice_vars[opt.get("value")] = var

        confirm_btn = ctk.CTkButton(
            choice_frame,
            text="✓ 确认选择",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.colors["primary"],
            height=26,
            command=self._on_multi_choice_confirm,
        )
        confirm_btn.grid(row=len(options), column=0, pady=(6, 0), sticky="w")

        choice_frame.grid(row=self._chat_row_count, column=0,
                          sticky="w", padx=(10, 60), pady=(0, 4))
        self._chat_row_count += 1
        self._active_options_frame = choice_frame

    def _on_multi_choice_confirm(self):
        """多选确认按钮：收集选中项并提交"""
        selected = [v for v, var in self._multi_choice_vars.items() if var.get()]
        if selected:
            display_text = "选择了：" + "、".join(selected)
            answer_text = ", ".join(selected)
        else:
            display_text = "未选择任何选项"
            answer_text = "未选择"

        self._add_user_message(display_text)
        self._cleanup_options_frame()

        self.send_btn.configure(state="disabled", text="⏳")
        self._v4_is_generating = True
        self._v4_controller.process_answer(answer_text)

    def _add_confirm_buttons(self, question_text: str):
        """确认提示：✓ 确认 和 ✗ 需要修改 两个按钮 (D-08)"""
        self._cleanup_options_frame()

        confirm_frame = ctk.CTkFrame(
            self.chat_scrollable,
            fg_color="transparent",
        )

        btn_confirm = ctk.CTkButton(
            confirm_frame,
            text="✓ 确认",
            fg_color=self.colors["success"],
            font=ctk.CTkFont(size=12),
            height=30,
            command=lambda: self._on_confirm_response(True, confirm_frame),
        )
        btn_confirm.grid(row=0, column=0, padx=(0, 4), pady=(0, 8))

        btn_modify = ctk.CTkButton(
            confirm_frame,
            text="✗ 需要修改",
            fg_color="#E74C3C",
            font=ctk.CTkFont(size=12),
            height=30,
            command=lambda: self._on_confirm_response(False, confirm_frame),
        )
        btn_modify.grid(row=0, column=1, padx=(4, 0), pady=(0, 8))

        confirm_frame.grid(row=self._chat_row_count, column=0,
                           sticky="w", padx=(10, 60), pady=(0, 4))
        self._chat_row_count += 1
        self._active_options_frame = confirm_frame

    def _on_confirm_response(self, confirmed: bool, frame):
        """确认/修改按钮点击处理"""
        if confirmed:
            self._add_user_message("确认")
            answer = "是"
        else:
            self._add_user_message("需要修改")
            answer = "需要修改"

        self._cleanup_options_frame()

        self.send_btn.configure(state="disabled", text="⏳")
        self._v4_is_generating = True
        self._v4_controller.process_answer(answer)

    # ================================================================
    # 事件处理
    # ================================================================

    def _on_v4_send(self):
        """发送按钮处理：添加用户气泡 → 调用 controller.process_input"""
        text = self.v4_input.get("1.0", "end-1c").strip()
        if not text or self._v4_is_generating:
            return

        self._add_user_message(text)
        self.v4_input.delete("1.0", "end")

        self._v4_set_generating(True)

        # process_input 内部根据 engine.state 自动路由
        self._v4_controller.process_input(text)

    def _on_v4_escape(self):
        """逃生门 (D-10)：跳过追问直接生成"""
        if self._v4_is_generating:
            return

        self._add_user_message("🎯 立即生成")
        self._v4_set_generating(True)
        self._v4_controller.skip_and_generate()

    def _v4_set_generating(self, generating: bool):
        """统一设置生成状态和按钮外观

        逃生门按钮始终保持可用（D-09）—— 用户可在任何交互类型中点击。
        _v4_is_generating 标志防止重复提交，不依赖按钮 disable 状态。
        """
        self._v4_is_generating = generating
        if generating:
            self.send_btn.configure(state="disabled", text="⏳")
        else:
            self.send_btn.configure(state="normal", text="▶")
            self.escape_btn.configure(state="normal")

    def _v4_on_state_change(self, data: dict):
        """引擎状态变更回调"""
        self.set_status(f"📋 状态：{data.get('state', '')}")

    def _v4_on_question(self, data: dict):
        """引擎发出追问/澄清回调 (D-08: 支持四种消息类型)"""
        question = data.get("question", {})
        question_text = question.get("question_text", data.get("message", ""))
        q_num = question.get("question_number", data.get("question_number", 0))
        max_q = question.get("max_questions", data.get("max_questions", 0))

        if q_num > 0:
            display_text = f"[{q_num}/{max_q}] {question_text}"
        else:
            display_text = question_text

        self._add_system_message(display_text)

        # 根据 question_type 渲染交互控件 (D-08)
        q_type = question.get("question_type", "text_input")
        options = question.get("options", [])

        if q_type == "single_choice" and options:
            self._add_single_choice_options(options)
        elif q_type == "multi_choice" and options:
            self._add_multi_choice_options(options)
        elif q_type == "confirm":
            self._add_confirm_buttons(question_text)
        else:
            # text_input — 用户在底部输入框自由回答，无需额外控件
            pass

        self._v4_set_generating(False)
        self.set_status("💬 请回答追问或点击「立即生成」跳过")

    def _v4_on_results(self, data: dict):
        """生成完成回调：保存结果 → 填充三卡 → 切换到结果页"""
        self.generated_prompts = data.get("prompts", {})
        self._populate_result_cards()
        self._switch_to_v4_page("results")
        self._v4_set_generating(False)
        self.set_status("✅ 已生成 3 个提示词方案")

    def _v4_on_error(self, data: dict):
        """错误回调"""
        self._v4_set_generating(False)
        self.set_status(f"❌ 出错：{data.get('error', '未知错误')}")
        from tkinter import messagebox
        messagebox.showerror("错误", f"生成出错：\n{data.get('error', '未知错误')}")

    def _on_v4_new_chat(self):
        """新对话 (D-05)：重置引擎 + 清空消息 + 新会话隔离"""
        self._v4_controller.reset()
        session_manager.new_session()

        for child in self.chat_scrollable.winfo_children():
            child.destroy()
        self._chat_row_count = 0
        self._messages = []
        self._add_welcome_message()

        self.v4_input.delete("1.0", "end")
        self.generated_prompts = None

        self._cleanup_options_frame()
        self._switch_to_v4_page("chat")
        self._v4_set_generating(False)
        self.set_status("🔄 新对话已开始，请输入你的需求")

    def _on_v4_back_to_chat(self):
        """返回对话 (D-04)：切回 chat 页，保留历史"""
        self._switch_to_v4_page("chat")
        self.set_status("💬 返回对话，可继续修改或补充信息")

    # ================================================================
    # Phase 6: V4 Result Page — 三卡横向对比 (Task 3)
    # ================================================================

    def _build_v4_result_page(self):
        """构建结果页面：header + 合规横幅 + 三卡横向对比 + 优化面板 (D-03, D-11~D-13)"""
        # Grid layout: row0=header, row1=compliance_banner (Task 3), row2=cards+panel
        self.result_frame.grid_rowconfigure(0, weight=0)
        self.result_frame.grid_rowconfigure(1, weight=0)
        self.result_frame.grid_rowconfigure(2, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)   # cards_area
        self.result_frame.grid_columnconfigure(1, weight=0)   # opt_panel (collapsible)

        # --- Header (row 0) ---
        h = ctk.CTkFrame(self.result_frame, height=60, corner_radius=0,
                         fg_color=self.colors["primary"])
        h.grid(row=0, column=0, columnspan=2, sticky="nsew")
        h.grid_propagate(False)
        h.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(h, text="🧠 智能提示词工坊 v4.0",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white").grid(row=0, column=0, padx=20, sticky="w")

        # Right button area
        btn_frame = ctk.CTkFrame(h, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=15, sticky="e")

        # Optimization panel toggle button (D-13)
        self.opt_toggle_btn = ctk.CTkButton(
            btn_frame, text="⚙️ 收起面板",
            font=ctk.CTkFont(size=12),
            fg_color="transparent", text_color="white",
            border_color="white", border_width=1,
            command=self._toggle_optimization_panel,
        )
        self.opt_toggle_btn.pack(side="left", padx=(0, 8))

        # Knowledge pack button (placeholder — wired in Task 3)
        self._v4_result_kb_btn = ctk.CTkButton(
            btn_frame, text="📚 知识包", width=80, height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", text_color="white",
            border_color="white", border_width=1,
            # command will be set in Task 3
        )
        self._v4_result_kb_btn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="← 返回对话",
                      font=ctk.CTkFont(size=12),
                      fg_color="transparent", text_color="white",
                      border_color="white", border_width=1,
                      command=self._on_v4_back_to_chat,
                      ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="🔄 新对话",
                      font=ctk.CTkFont(size=12),
                      fg_color="#1A3F6D", text_color="white",
                      command=self._on_v4_new_chat,
                      ).pack(side="left")

        # Compliance banner (row 1) — built by Task 3, hidden by default
        self.compliance_banner = ctk.CTkFrame(
            self.result_frame, fg_color="#FFF3CD", corner_radius=6,
            border_width=1, border_color="#FFC107"
        )
        self.compliance_banner.grid(row=1, column=0, columnspan=2,
                                    padx=12, pady=(4, 0), sticky="ew")
        self.compliance_banner.grid_remove()  # default hidden

        ctk.CTkLabel(self.compliance_banner, text="⚖️",
                     font=ctk.CTkFont(size=16)).pack(side="left", padx=(12, 6), pady=6)
        self.compliance_label = ctk.CTkLabel(
            self.compliance_banner, text="",
            font=ctk.CTkFont(size=12), text_color="#856404",
            wraplength=700, justify="left",
        )
        self.compliance_label.pack(side="left", padx=(0, 12), pady=6)

        # --- Cards area (row 2, column 0) ---
        self.cards_area = ctk.CTkFrame(self.result_frame,
                                       fg_color=self.colors["body"])
        self.cards_area.grid(row=2, column=0, sticky="nsew", padx=12, pady=12)
        self.cards_area.grid_columnconfigure((0, 1, 2), weight=1, uniform="card_col")
        self.cards_area.grid_rowconfigure(0, weight=1)

        # Build three strategy cards
        self._result_cards = {}
        strategies_order = ["direct", "roleplay", "detailed"]

        for col, sk in enumerate(strategies_order):
            card = ctk.CTkFrame(self.cards_area, fg_color="white",
                                corner_radius=8, border_width=1,
                                border_color="#DEE2E6")
            card.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(1, weight=1)

            # Title row
            title_text = STRATEGIES[sk]["name"]
            title_color = STRATEGIES[sk]["color"]
            tag_text = STRATEGIES[sk]["tag"]

            title_frame = ctk.CTkFrame(card, fg_color="transparent")
            title_frame.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")

            ctk.CTkLabel(title_frame, text=title_text,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=self.colors["text"]
                         ).pack(side="left")

            ctk.CTkLabel(title_frame, text=tag_text,
                         font=ctk.CTkFont(size=10),
                         text_color="white", fg_color=title_color,
                         corner_radius=4,
                         ).pack(side="right", padx=(8, 0))

            # Textbox (read-only, row 1, weight=1)
            textbox = ctk.CTkTextbox(
                card, wrap="word",
                font=ctk.CTkFont(size=12, family="Microsoft YaHei"),
                fg_color="white", border_width=0, corner_radius=4,
                state="disabled",
            )
            textbox.grid(row=1, column=0, padx=12, pady=8, sticky="nsew")

            # Copy button (row 2)
            copy_btn = ctk.CTkButton(
                card, text="📋 复制",
                font=ctk.CTkFont(size=11),
                fg_color=self.colors["success"], hover_color="#1E8449",
                height=28,
                command=lambda k=sk: self._on_v4_copy_card(k),
            )
            copy_btn.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

            self._result_cards[sk] = {
                "card": card,
                "textbox": textbox,
                "copy_btn": copy_btn,
            }

        # --- Optimization panel (row 2, column 1) — built after cards ---
        self._panel_visible = True
        self._opt_constraint_vars = []
        self._build_optimization_panel()

    def _build_optimization_panel(self):
        """构建右侧优化侧栏面板 (D-11/D-12/D-13)

        包含：追加要求输入框、换风格下拉、加限制复选框、重新生成按钮
        """
        opt_panel = ctk.CTkFrame(
            self.result_frame, fg_color="white", corner_radius=8,
            border_width=1, border_color=self.colors["border"],
            width=280,
        )
        opt_panel.grid(row=2, column=1, padx=(6, 12), pady=6, sticky="nsew")
        opt_panel.grid_propagate(False)
        # Prevent opt_panel from collapsing to zero height
        opt_panel.grid_rowconfigure(4, weight=1)

        # A. Title
        ctk.CTkLabel(
            opt_panel, text="⚙️ 优化提示词",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"],
        ).grid(row=0, column=0, padx=16, pady=(14, 8), sticky="w")

        # B. 追加要求
        ctk.CTkLabel(
            opt_panel, text="📝 追加要求",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text"],
        ).grid(row=1, column=0, padx=16, pady=(4, 2), sticky="w")

        self.refine_input = ctk.CTkTextbox(
            opt_panel, height=80, wrap="word",
            font=ctk.CTkFont(size=12),
            fg_color="#F8F9FA",
        )
        self.refine_input.grid(row=2, column=0, padx=16, pady=(0, 8), sticky="ew")

        # C. 换风格
        ctk.CTkLabel(
            opt_panel, text="🎨 换风格",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text"],
        ).grid(row=3, column=0, padx=16, pady=(4, 2), sticky="w")

        self.style_combo = ctk.CTkComboBox(
            opt_panel,
            values=["保持当前风格", "更简洁", "更详细", "更专业", "更通俗"],
            state="readonly",
            font=ctk.CTkFont(size=12),
        )
        self.style_combo.set("保持当前风格")
        self.style_combo.grid(row=4, column=0, padx=16, pady=(0, 8), sticky="ew")

        # D. 加限制
        ctk.CTkLabel(
            opt_panel, text="🔒 加限制",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text"],
        ).grid(row=5, column=0, padx=16, pady=(4, 2), sticky="w")

        constraint_frame = ctk.CTkFrame(opt_panel, fg_color="transparent")
        constraint_frame.grid(row=6, column=0, padx=16, pady=(0, 8), sticky="ew")

        # Store (checkbox, var) tuples
        self._opt_constraint_vars = []
        constraint_labels = [
            "限制字数（≤500字）",
            "包含示例/案例",
            "纯文本（无表格/代码块）",
        ]
        for label in constraint_labels:
            var = tk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                constraint_frame,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text"],
            )
            cb.pack(anchor="w", pady=2)
            self._opt_constraint_vars.append((cb, var))

        # E. Spacer to push button to bottom
        opt_panel.grid_rowconfigure(7, weight=1)

        # F. 重新生成按钮
        self.opt_regenerate_btn = ctk.CTkButton(
            opt_panel, text="🔄 重新生成",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors["primary"],
            height=36,
            command=self._on_opt_regenerate,
        )
        self.opt_regenerate_btn.grid(
            row=8, column=0, padx=16, pady=(8, 14), sticky="ew"
        )

        self.opt_panel = opt_panel

    def _toggle_optimization_panel(self):
        """收起/展开优化面板 (D-13)"""
        if self._panel_visible:
            # Collapse: remove panel, let cards fill space
            self.opt_panel.grid_remove()
            self.result_frame.grid_columnconfigure(1, weight=0, minsize=0)
            self.opt_toggle_btn.configure(text="◀ 展开面板")
            self._panel_visible = False
        else:
            # Expand: restore panel
            self.opt_panel.grid()
            self.result_frame.grid_columnconfigure(1, weight=0, minsize=280)
            self.opt_toggle_btn.configure(text="⚙️ 收起面板")
            self._panel_visible = True

    def _on_opt_regenerate(self):
        """优化面板重新生成按钮处理 (D-12)

        收集参数 → 后台线程调用 refine_prompts → UI 线程更新三卡
        """
        if self._v4_is_generating:
            return

        # Collect parameters
        additional = self.refine_input.get("1.0", "end-1c").strip()
        style = self.style_combo.get()
        constraints = [
            cb.cget("text") for cb, var in self._opt_constraint_vars if var.get()
        ]

        # Disable button with loading state
        self.opt_regenerate_btn.configure(
            state="disabled", text="⏳ 优化中..."
        )
        self._v4_is_generating = True

        def _do_refine():
            try:
                prompts = self._v4_controller.refine_prompts(
                    additional_reqs=additional,
                    style=style if style != "保持当前风格" else None,
                    constraints=constraints,
                )
                self.root.after(0, lambda: self._v4_on_refined(prompts))
            except Exception as e:
                self.root.after(0, lambda: self._v4_on_error({"error": str(e)}))

        thread = threading.Thread(target=_do_refine, daemon=True)
        thread.start()

    def _v4_on_refined(self, prompts: dict):
        """优化重新生成完成回调：更新三卡 + 合规横幅"""
        self.generated_prompts = prompts
        self._populate_result_cards()
        self._update_compliance_banner()
        self._v4_set_generating(False)
        self.opt_regenerate_btn.configure(
            state="normal", text="🔄 重新生成"
        )
        self.set_status("✅ 优化完成，已重新生成 3 个提示词方案")

    def _update_compliance_banner(self):
        """根据当前结果的行业更新合规横幅显隐 (QA-03)"""
        try:
            if hasattr(self, '_v4_controller') and self._v4_controller is not None:
                industry_id = self._v4_controller._engine._last_analysis.get("industry_id", "")
            else:
                industry_id = ""
        except Exception:
            industry_id = ""

        # Also check generated prompts for compliance keywords (backward compat)
        has_compliance_text = False
        if self.generated_prompts:
            sample = next(iter(self.generated_prompts.values()), "")
            has_compliance_text = "合规声明" in sample or "不构成投资建议" in sample

        banner_texts = {
            "finance": "金融行业内容 — 本提示词仅供专业参考，不构成投资建议。涉及金融建议请以持牌机构正式意见为准。",
            "manufacturing": "制造行业内容 — 本提示词仅供技术参考。涉及安全规范请以国家/行业标准为最终依据。",
        }

        if industry_id in banner_texts or has_compliance_text:
            text = banner_texts.get(industry_id, "")
            if text:
                self.compliance_label.configure(text=text)
                self.compliance_banner.grid()
            else:
                self.compliance_banner.grid_remove()
        else:
            self.compliance_banner.grid_remove()

    def _populate_result_cards(self):
        """填充三张策略卡的内容，同时更新合规横幅"""
        if not self.generated_prompts:
            return
        for sk, info in self._result_cards.items():
            prompt = self.generated_prompts.get(sk, "暂未生成")
            textbox = info["textbox"]
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", prompt)
            textbox.configure(state="disabled")

        # Update compliance banner based on generated content
        self._update_compliance_banner()

    def _on_v4_copy_card(self, strategy_key: str):
        """复制单张策略卡内容到剪贴板 (D-03)"""
        prompt = self.generated_prompts.get(strategy_key, "")
        if not prompt:
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(prompt)

        # Button feedback animation
        copy_btn = self._result_cards[strategy_key]["copy_btn"]
        copy_btn.configure(text="✅ 已复制", fg_color=self.colors["secondary"])
        self.root.after(2000, lambda: copy_btn.configure(
            text="📋 复制", fg_color=self.colors["success"]))

        sn = STRATEGIES[strategy_key]["name"]
        self.set_status(f"✅ 已复制：{sn}")

    def run(self):
        self.root.mainloop()
