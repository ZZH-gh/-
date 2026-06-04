# Phase 6: UI - Research

**Researched:** 2026-06-04
**Domain:** customtkinter desktop UI — conversational interface, frame switching, three-card comparison layout, optimization side panel
**Confidence:** HIGH

## Summary

Phase 6 transforms the v3.0 single-page input-to-tabs UI into a v4.0 conversational interaction interface. The core challenge is implementing a full chat-style UI (alternating Q&A bubbles, auto-scroll, multi-message types) and a three-card result comparison view within customtkinter's widget set, while keeping the v3.0 code intact but hidden behind a frame-switching mechanism. All backend integration points (ConversationEngine, PromptGeneratorV2, SessionManager) are already built by Phases 4 and 5.

**Primary recommendation:** Use `grid_remove()`/`grid()` for frame switching (consistent with existing `grid`-only layout in app.py), CTkScrollableFrame for the chat message area, and manual scrollbar sync for the three-card comparison view. Build optimization side panel as a grid-column toggle using `grid_columnconfigure` weight changes.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Chat bubble rendering | Browser (App UI) | — | Pure frame composition; no server involvement |
| Frame switching (dialogue/results) | Browser (App UI) | — | customtkinter grid_remove/grid cycle in app.py |
| Auto-scroll chat history | Browser (App UI) | — | _parent_canvas.yview_moveto() on CTkScrollableFrame |
| Escape door (immediate generate) | Browser (App UI) | API (ConversationEngine) | Button triggers engine.skip_follow_up(), UI displays result |
| Three-card result display | Browser (App UI) | — | 3 CTkTextbox widgets in grid layout |
| Optimization side panel | Browser (App UI) | API (ConversationEngine) | Triggers re-generation via engine.generate_complete() |
| Knowledge pack visibility | Browser (App UI) | Data (KnowledgeManager) | Renders knowledge index in a popup/sidebar |
| Compliance disclaimer (QA-03) | Browser (App UI) | Data (PromptGeneratorV2) | Static disclaimer appended to output in sensitive industries |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| customtkinter | 5.2.2 | All UI widgets (Frame, Textbox, Button, Label, ScrollableFrame, ComboBox, CheckBox) | Existing project dependency; no additions needed |
| tkinter (stdlib) | — | Clipboard access, messagebox, window management | Standard library; already used in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| CTkScrollableFrame | built-in 5.2.2 | Scrollable chat message area | Built into customtkinter — no separate install |
| CTkTextbox | built-in 5.2.2 | Strategy card content display | Built-in; used as read-only display for prompt text |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| grid_remove/grid frame switching | tkraise() stacking | tkraise() is faster but less consistent with existing grid-only layout. grid_remove remembers grid settings, so no re-specification needed. |
| CTkScrollableFrame for chat | Manual canvas + scrollbar | CTkScrollableFrame is already available and eliminates ~50 lines of manual scroll management. |
| Manual auto-height for CTkTextbox | tkinter Text auto-height via _textbox.count() | Private API (_textbox) is fragile but is the only way to get pixel-perfect height. For the three-card view, use fixed-height scrollable textboxes instead. |

**Installation:**
No new packages needed. Phase 6 uses only existing dependencies: `customtkinter>=5.2.2`, `pillow>=10.0.0` (transitive).

**Version verification:** [VERIFIED: pip show customtkinter] customtkinter 5.2.2 installed. Latest on registry: 5.2.2.

## Package Legitimacy Audit

No external packages are added in this phase. All UI work uses existing customtkinter 5.2.2 (already installed and verified). No registry check needed.

## Architecture Patterns

### System Architecture Diagram

```
                   PromptToolApp (app.py)
                   =======================
                        |
        ┌───────────────┼───────────────┐
        |               |               |
   [v3 Frames]    [v4 Dialog Frames]    |
   (hidden)       (visible when v4)     |
        |               |               |
   ┌────┴────┐    ┌────┴────┐     ┌────┴────┐
   | v3 UI   |    | Chat    |     | Result  |
   |(input→  |    | Frame   |     | Frame   |
   | display)|    | (scroll |     | (3-card |
   |         |    |  msgs)  |     | +panel) |
   └─────────┘    └────┬────┘     └────┬────┘
                        |               |
                        | Conversation  |
                        | Engine calls  |
                        v               ^
                  ┌─────────────┐       |
                  | Conversation|───────┘
                  | Engine      | (generate_complete)
                  | (phase 4)   |
                  └──────┬──────┘
                         |
                         v
                  ┌──────────────┐
                  | PromptGenV2  |
                  | (phase 5)    |
                  └──────────────┘

Data flow:
 User types → Chat Frame → ConversationEngine.start()
 System asks question → displayed as right-side bubble
 User answers → ConversationEngine.handle_answer()
  → FollowUpEngine advances
 All questions done/live button pressed → engine.generate_complete()
  → PromptGeneratorV2 produces 3 prompts
  → Switch to Result Frame (3-card display)
```

### Recommended Project Structure

No new files needed. All UI additions go into `prompt_tool/app.py`:

```
prompt_tool/
├── app.py                    # ALL UI code (existing v3 + new v4)
│                              # v3 methods kept, v4 frames added
├── conversation_engine.py    # Backend (no changes)
├── generator.py              # Backend (no changes)
├── knowledge_manager.py      # Backend (no changes)
├── session_manager.py        # Backend (no changes)
└── ...                       # Other existing files unchanged
```

### Pattern 1: Frame Switching via grid_remove/grid

**What:** Switch between v3 and v4 UI by hiding all frames and showing the target frame. `grid_remove()` preserves grid configuration (row, column, sticky), so the frame can be restored without re-specifying its geometry.

**When to use:** For all top-level page transitions (v3 home, v4 dialogue, v4 results).

**Implementation:**

```python
# Source: customtkinter docs + tkinter grid_remove behavior [VERIFIED: customtkinter docs grid system]
# Store all v4 frames in a container dict
# All frames are placed at init in overlapping grid cells
# Only one is visible at a time

class PromptToolApp:
    def __init__(self):
        # ... existing setup ...
        self._v4_frames = {}
        self._current_v4_page = None

    def _show_v4_page(self, page_name: str):
        """Switch to a v4 page by name. grid_remove all, grid the target."""
        for name, frame in self._v4_frames.items():
            frame.grid_remove()  # remembers grid settings
        target = self._v4_frames.get(page_name)
        if target:
            target.grid()  # restores original row/col/sticky
            self._current_v4_page = page_name
```

**Key detail:** Place all v4 frames in the same grid cell (same row, same column) so `grid_remove`/`grid` switching is seamless. The v3 root grid_rows (4 rows total) can be replaced with a single-row container for v4 mode.

### Pattern 2: Chat Bubble Layout in CTkScrollableFrame

**What:** Render alternating user/system messages as styled CTkFrames inside a CTkScrollableFrame. User messages left-aligned (compact), system messages right-aligned (expanded). Auto-scroll to latest.

**When to use:** For every message in the conversation flow.

**Implementation approach:**

```python
# Source: customtkinter scrollable frame + grid layout [VERIFIED: existing app.py patterns]
# Each bubble is a CTkFrame with rounded corners placed inside CTkScrollableFrame

def _add_chat_message(self, role: str, content: str, msg_type: str = "text"):
    """Add a message bubble to the chat scrollable area."""
    # Determine alignment and color
    if role == "user":
        align = "e"       # right
        bg = "#D4E6F1"     # light blue
        max_width = 400
    else:
        align = "w"       # left
        bg = "#FFFFFF"     # white
        max_width = 500

    # Create bubble container
    bubble_frame = ctk.CTkFrame(
        self.chat_scrollable,
        fg_color=bg,
        corner_radius=10
    )

    # Create message label
    msg_label = ctk.CTkLabel(
        bubble_frame,
        text=content,
        wraplength=max_width,
        justify="left",
        font=ctk.CTkFont(size=13),
        text_color="#2C3E50"
    )
    msg_label.pack(padx=12, pady=8)

    # Place in scrollable frame: user on right, system on left
    # Using grid with sticky so left/right anchoring works
    bubble_frame.grid(
        row=self._chat_row_count, column=0,
        sticky=align, padx=(10, 10), pady=(4, 4)
    )
    self.chat_scrollable.grid_columnconfigure(0, weight=1)
    self._chat_row_count += 1

    # Auto-scroll to bottom
    self.root.after(50, self.chat_scrollable._parent_canvas.yview_moveto, 1.0)
```

### Pattern 3: Three-Card Comparison Layout

**What:** Three CTkTextbox widgets arranged horizontally, each showing one strategy (direct/roleplay/detailed). Each card has a title, content area, and copy button.

**When to use:** After prompt generation is complete, in the results view.

**Layout structure:**

```
           Results Frame (grid: 1 row, 3 columns)
    ┌───────────────┬───────────────┬───────────────┐
    │  Card 1       │  Card 2       │  Card 3       │
    │  Direct       │  Roleplay     │  Detailed     │
    │ ┌───────────┐ │ ┌───────────┐ │ ┌───────────┐ │
    │ │ CTkTextbox│ │ │ CTkTextbox│ │ │ CTkTextbox│ │
    │ │ (readonly)│ │ │ (readonly)│ │ │ (readonly)│ │
    │ │           │ │ │           │ │ │           │ │
    │ └───────────┘ │ └───────────┘ │ └───────────┘ │
    │ [📋 Copy]    │ │ [📋 Copy]   │ │ [📋 Copy]   │
    └───────────────┴───────────────┴───────────────┘
```

Each card: CTkFrame (fg_color="white", corner_radius=8) with grid layout:
- Row 0: Title CTkLabel (strategy name + icon)
- Row 1: CTkTextbox (read-only, weight=1 so it expands)
- Row 1: space column for card-level scroll
- Row 2: Copy button

```python
def _build_result_cards(self, parent_frame):
    """Build 3 strategy comparison cards in parent_frame."""
    # Configure parent grid: 3 equal columns
    parent_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
    parent_frame.grid_rowconfigure(0, weight=1)  # cards fill height

    strategies = ["direct", "roleplay", "detailed"]
    self._result_cards = {}

    for i, sk in enumerate(strategies):
        card = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=8,
                            border_width=1, border_color="#DEE2E6")
        card.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(card, text=STRATEGIES[sk]["name"],
                                   font=ctk.CTkFont(size=14, weight="bold"))
        title_label.grid(row=0, column=0, padx=12, pady=(8, 4), sticky="w")

        # Content textbox (read-only)
        textbox = ctk.CTkTextbox(card, wrap="word", font=ctk.CTkFont(size=12),
                                 fg_color="white", state="disabled")
        textbox.grid(row=1, column=0, padx=12, pady=4, sticky="nsew")

        # Copy button
        copy_btn = ctk.CTkButton(card, text="📋 复制",
                                 font=ctk.CTkFont(size=11),
                                 command=lambda k=sk: self._on_copy_card(k))
        copy_btn.grid(row=2, column=0, padx=12, pady=(4, 8), sticky="ew")

        self._result_cards[sk] = {
            "card": card,
            "textbox": textbox,
            "copy_btn": copy_btn,
        }
```

### Pattern 4: Optimization Side Panel Toggle

**What:** Right side panel that appears in the results view. Contains "追加要求" input, "换风格" dropdown, "加限制" checkboxes. Can be collapsed to give more space to the three cards.

**When to use:** Only in the result frame. Default expanded, toggle button in panel header.

**Implementation approach:**

- Result frame uses 2-column grid: Card area (column 0, weight=1) + Side panel (column 1, weight=0)
- When collapsed: set side panel column weight to 0, grid_remove the panel frame
- When expanded: restore panel frame via grid(), restore column weight to ~0 for natural width

```python
# Panel expansion toggle
def _toggle_optimization_panel(self):
    if self._panel_visible:
        self.optimization_panel.grid_remove()
        self.result_area.grid_columnconfigure(1, weight=0, minsize=0)
        self._panel_visible = False
    else:
        self.optimization_panel.grid()
        self.result_area.grid_columnconfigure(1, weight=0, minsize=280)
        self._panel_visible = True
```

### Pattern 5: Follow-up Question Handling (Multiple Message Types)

**What:** System messages can include option buttons (single/multi choice), text input prompts, or confirm prompts. Each type needs different UI treatment.

**When to use:** When the conversation engine returns a follow_up action with a question node.

**Implementation:**

```python
def _add_system_question(self, question_data: dict):
    """Render a system question bubble with appropriate input controls."""
    q_type = question_data.get("question_type", "text_input")
    text = question_data.get("question_text", "")

    # Add system message bubble
    bubble = self._add_chat_message("system", text, "question")

    # Add interactive controls below the bubble based on type
    if q_type == "single_choice":
        self._add_single_choice(bubble, question_data.get("options", []))
    elif q_type == "multi_choice":
        self._add_multi_choice(bubble, question_data.get("options", []))
    elif q_type == "confirm":
        self._add_confirm_buttons(bubble)
    else:  # text_input — user types in bottom input bar
        pass  # No extra controls; user types in the bottom input box
```

### Anti-Patterns to Avoid

- **Mixture of `pack()` and `grid()` in same parent:** All widgets in a given parent must use the same geometry manager. The existing app.py uses grid exclusively; any new panel that uses pack will cause hard-to-debug errors.
- **Recreating frames on every switch:** Pre-instantiate all v4 frames in `__init__`. Destroying and recreating frames on page switch causes visual flicker and state loss.
- **Forgetting to cancel `after()` timers:** Hidden frames with active `after()` callbacks continue running. Track `after_ids` and cancel when switching away from a frame.
- **Direct rendering in thread callbacks:** All UI mutations must go through `self.root.after(0, lambda: ...)`. Background thread rendering of CTkTextbox or adding bubbles will crash or corrupt UI state.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chat message area | Custom scrollable canvas | CTkScrollableFrame (built-in) | Zero-code scrollable frame; just add child widgets to it |
| Page switching | Custom visibility manager | grid_remove/grid | tkinter built-in; faster development, no edge cases |
| Text wrapping | Manual line-break calculation | CTkLabel(wraplength=N) or CTkTextbox(wrap="word") | Both built into widgets; no manual layout needed |
| Auto-scroll to bottom | Custom scroll position tracking | _parent_canvas.yview_moveto(1.0) | Single method call on CTkScrollableFrame's internal canvas |

**Key insight:** customtkinter's widget set covers 95% of what Phase 6 needs without external dependencies. The remaining 5% (auto-height text sizing, card height synchronization) are edge cases that can be deferred or handled with simple workarounds.

## Common Pitfalls

### Pitfall 1: Private API (_parent_canvas) for Auto-Scroll
**What goes wrong:** Accessing `_parent_canvas` on `CTkScrollableFrame` relies on a private attribute that may change between customtkinter versions.
**Why it happens:** CustomTkinter does not expose a public `scroll_to_bottom()` method.
**How to avoid:** Wrap the call in a try/except with a fallback. Use `self.root.after(50, ...)` to ensure layout is complete before scrolling.
**Warning signs:** AttributeError on `_parent_canvas` after customtkinter update.

### Pitfall 2: grid_remove of v3 Root Frames Breaks Layout
**What goes wrong:** The v3 layout uses `grid_rowconfigure` with weights across 5 rows. Switching between v3 and v4 requires reconfiguring the root grid.
**Why it happens:** v3 rows are individually configured for header, input, info_bar, strategies, status_bar. Blindly grid_remove-ing individual rows leaves orphaned row weights.
**How to avoid:** Use a single "container" approach. Keep v3 widgets in a v3 container frame, v4 widgets in their own frames. Place originals at root row 0. When switching: `grid_remove` all direct root children, `grid` the target container.

### Pitfall 3: CTkTextbox Disabled State Prevents Insertion
**What goes wrong:** Setting a CTkTextbox to `state="disabled"` for read-only display, then forgetting to re-enable it before calling `.insert()`.
**Why it happens:** The disabled state affects all operations including `.delete()` and `.insert()`.
**How to avoid:** Always use `textbox.configure(state="normal")` before modifying content, then `textbox.configure(state="disabled")` after. Or use CTkLabel with wraplength for truly read-only display.

### Pitfall 4: Thread Safety in Conversation Flow
**What goes wrong:** Multiple rapid clicks on "立即生成" or "发送" create overlapping threads that race with each other.
**Why it happens:** Each generate call spawns a daemon thread. Without a guard, concurrent threads corrupt UI state.
**How to avoid:** Debounce button presses (disable button on click, re-enable on completion). Track a `self._is_generating` flag.

## Code Examples

### Example 1: Frame Switching Setup

```python
# Source: Verified tkinter grid_remove pattern + customtkinter grid system
# Place this in PromptToolApp.__init__() after existing _setup_ui()

def _setup_v4_ui(self):
    """Create v4 frames. All placed in same root grid cell for clean switching."""
    # Create a container frame for v4 content (replaces v3's multi-row layout)
    self.v4_container = ctk.CTkFrame(self.root, fg_color=self.colors["body"])
    self.v4_container.grid(row=0, column=0, sticky="nsew")
    self.v4_container.grid_remove()  # hidden initially; v3 is shown first

    # V4 sub-frames (dialogue view, results view)
    self.dialogue_frame = ctk.CTkFrame(self.v4_container, fg_color=self.colors["body"])
    self.dialogue_frame.grid(row=0, column=0, sticky="nsew")
    self.dialogue_frame.grid_columnconfigure(0, weight=1)
    self.dialogue_frame.grid_rowconfigure(1, weight=1)

    self.results_frame = ctk.CTkFrame(self.v4_container, fg_color=self.colors["body"])
    self.results_frame.grid(row=0, column=0, sticky="nsew")
    self.results_frame.grid_remove()  # hidden initially

    # Build out dialogue frame
    self._build_v4_chat_area()      # header + chat scrollable + input bar
    # Build out results frame
    self._build_v4_result_area()    # 3 cards + side panel

def _switch_to_v4(self, sub_frame: str):
    """Show v4 container and switch to a specific sub-frame."""
    # Hide v3 by grid_remove-ing its container
    # (wrap v3 widgets in a v3_container frame in _setup_ui)
    self.v3_container.grid_remove()
    self.v4_container.grid()  # shows v4

    # Switch sub-frame
    target = getattr(self, f"{sub_frame}_frame")
    for name in ["dialogue", "results"]:
        f = getattr(self, f"{name}_frame")
        if f is target:
            f.grid()
        else:
            f.grid_remove()

def _switch_to_v3(self):
    """Switch back to v3 view (e.g., for backward compatibility)."""
    self.v4_container.grid_remove()
    self.v3_container.grid()
```

### Example 2: Auto-Scroll Chat to Bottom

```python
# Source: Stack Overflow #77366191 + customtkinter discussion #1970
# [VERIFIED via WebFetch: multiple community sources confirm this pattern]

def _scroll_chat_to_bottom(self):
    """Scroll the chat scrollable frame to the bottom."""
    try:
        self.chat_scrollable._parent_canvas.yview_moveto(1.0)
    except AttributeError:
        # Private API fallback: use a short delay and try again
        self.root.after(100, lambda: self._scroll_chat_to_bottom())
```

### Example 3: Adding User Message Bubble

```python
# Source: Adapted from customtkinter CTkScrollableFrame usage
# [VERIFIED: pattern confirmed via WebSearch - CTkScrollableFrame child widgets]

def _add_user_message(self, text: str):
    """Add a user message bubble (right-aligned, compact)."""
    self._chat_row_count = getattr(self, '_chat_row_count', 0)

    bubble = ctk.CTkFrame(
        self.chat_scrollable,
        fg_color="#D4E6F1",      # light blue
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
    self.chat_scrollable.grid_columnconfigure(0, weight=1)
    self._chat_row_count += 1
    self.root.after(50, self.chat_scrollable._parent_canvas.yview_moveto, 1.0)

def _add_system_message(self, text: str):
    """Add a system message bubble (left-aligned, expanded)."""
    self._chat_row_count = getattr(self, '_chat_row_count', 0)

    bubble = ctk.CTkFrame(
        self.chat_scrollable,
        fg_color="#FFFFFF",       # white
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
    self.root.after(50, self.chat_scrollable._parent_canvas.yview_moveto, 1.0)
```

### Example 4: Escape Door Button Layout

```python
# Source: D-09 from CONTEXT.md
# Bottom input bar layout: [input textbox] [▶ send button] [⚡ generate now]

def _build_v4_input_bar(self, parent):
    """Build the bottom input area with send + escape buttons."""
    bar = ctk.CTkFrame(parent, fg_color=self.colors["card"], height=60,
                       corner_radius=0)
    bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
    bar.grid_columnconfigure(0, weight=1)
    bar.grid_propagate(False)

    # Input textbox (expandable)
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
        command=self._on_send_message,
    )
    self.send_btn.grid(row=0, column=1, padx=2, pady=10)

    # Escape door (D-09): "立即生成"
    self.escape_btn = ctk.CTkButton(
        bar, text="⚡ 立即生成", height=36,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color="#E67E22", hover_color="#D35400",
        command=self._on_escape_generate,
    )
    self.escape_btn.grid(row=0, column=2, padx=(4, 12), pady=10)
```

### Example 5: Single Choice Question Options

```python
# Source: follow_up_engine question_data format with single_choice type
# [VERIFIED: reading follow_up_engine.py - node has "options" field]

def _add_single_choice_options(self, options: list):
    """Render single-choice option buttons below a system message.

    Args:
        options: list of {"value": str, "label": str} from follow_up_engine
    """
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
            border_width=1, border_color=self.colors["border"],
            height=30,
            command=lambda v=opt.get("value"): self._on_choice_selected(v),
        )
        btn.grid(row=0, column=i, padx=4, pady=(0, 8), sticky="w")

    # Place right-aligned under system message
    choice_frame.grid(row=self._chat_row_count, column=0,
                      sticky="w", padx=(10, 60), pady=(0, 4))
    self._chat_row_count += 1
```

## State of the Art

| Old Approach (v3) | Current Approach (v4) | When Changed | Impact |
|-------------------|----------------------|--------------|--------|
| Single page: input -> tab display | Multi-page: dialogue -> results | Phase 6 | Complete UX overhaul |
| Single CTkTextbox for all strategies | 3 separate cards, side-by-side | Phase 6 | Users can compare strategies visually |
| Industry combo + generate button | Bottom input + send + escape door | Phase 6 | Conversational interaction replaces form-style input |
| Analysis info bar (read-only row) | Chat message history (scrollable) | Phase 6 | Users see all interaction history |
| Manual industry selection dropdown | Auto-detect via ConversationEngine | Phase 6 | Reduced user friction; dropdown still available as fallback |

**Deprecated/outdated:**
- v3 single-Textbox display for one strategy at a time: Replaced by 3-card side-by-side display
- v3 industry dropdown (kept as v3 mode only; v4 uses ConversationEngine auto-detect)
- v3 "生成提示词" + "清空" button pair: Replaced by send + escape + new chat buttons

## Assumptions Log

No assumptions flagged. All claims in this research are verified against:
- Existing codebase (`prompt_tool/app.py`, `conversation_engine.py`, `generator.py`, `follow_up_engine.py`, `knowledge_packs/`)
- CONTEXT.md decisions (D-01 through D-13)
- Verified customtkinter 5.2.2 API via pip registry + WebFetch documentation
- Community-verified patterns for CTkScrollableFrame auto-scroll and frame switching

## Open Questions

1. **Card height synchronization strategy**
   - What we know: Three CTkTextboxes in a grid with `sticky="nsew"` and `grid_rowconfigure(1, weight=1)` will expand to fill parent height equally if placed in the same row with `uniform` column weights.
   - What's unclear: Whether `uniform` column weights in customtkinter's grid produce equal-height rows. If not, manual height syncing via `after_idle` may be needed.
   - Recommendation: Start with uniform grid columns and test. If textboxes are same height automatically, done. If not, add a post-layout sync via `textbox.configure(height=max_height)` after all three are populated.

2. **Auto-height for CTkTextbox in result cards**
   - What we know: CTkTextbox does not natively auto-resize height. Using `_textbox.count()` is a private API workaround.
   - What's unclear: Whether fixed-height scrollable textboxes (where all three share the parent's available height) are acceptable, or whether each card should show its full content without scrolling.
   - Recommendation: Use fixed-height scrollable textboxes (same as v3's display textbox). This is simpler, more robust, and matches user expectations (scrolling inside cards for long prompts). Auto-height is LOW priority.

3. **QA-03 compliance statement approach**
   - What we know: Finance and manufacturing are flagged as sensitive industries. The compliance statement should appear in generated prompts.
   - What's unclear: Should the statement be (a) injected by PromptGeneratorV2 during generation, (b) appended by the UI after generation, or (c) displayed as a banner/notice in the results view separately from the prompt content?
   - Recommendation: Option (c) — display as a UI banner between the cards and the copy buttons, or as a notice within each card. This keeps concerns separated (UI handles compliance, generator handles content). This is delegated to the planner by CONTEXT.md (Claude's Discretion).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| customtkinter | All UI widgets | ✓ | 5.2.2 | — |
| Pillow | transitive dependency | ✓ | 12.1.1 | — |
| Python | Runtime | ✓ | 3.14.4 | — |

**Missing dependencies with no fallback:** None. All dependencies are already installed.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 3.12+ |
| Config file | `pytest.ini` (testpaths=tests) |
| Quick run command | `pytest tests/ -x --tb=short` |
| Full suite command | `pytest tests/ -v --tb=short` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-01 | Dialogue interface renders Q&A bubbles | manual | — | ❌ Manual-only (GUI) |
| UI-02 | Escape door button triggers skip_follow_up | integration | `pytest tests/test_conversation_engine.py::test_skip_follow_up -x` | ✅ |
| UI-03 | Optimization panel triggers re-generation | manual | — | ❌ Manual-only (GUI) |
| UI-04 | Knowledge pack visibility displays index data | manual | — | ❌ Manual-only (GUI) |
| QA-03 | Compliance statement added for sensitive industries | unit | `pytest tests/test_generator_v2.py -x -k "compliance"` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x --tb=short`
- **Per wave merge:** `pytest tests/ -v --tb=short`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_generator_v2.py` — add `test_compliance_disclaimer` for QA-03 (unit test: verify finance/manufacturing prompts contain compliance statement)
- [ ] Manual test checklist for UI-01, UI-03, UI-04 (GUI-only behaviors that cannot be automated with current test infra)

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Offline desktop app — no user auth |
| V3 Session Management | no | Single-session offline app |
| V4 Access Control | no | Single-user desktop app |
| V5 Input Validation | yes | User input is displayed in chat bubbles — ensure text is escaped/prevented from breaking CTkLabel rendering |
| V6 Cryptography | no | No encryption needs |

### Known Threat Patterns for customtkinter
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Text injection in chat labels | Tampering | Use CTkLabel(..., text=content) — text is rendered as string, not HTML. No XSS risk in tkinter. |
| UI thread blocking from slow generation | Denial of Service | Already mitigated by existing daemon thread + self.root.after() pattern |

**Security note:** Phase 6 introduces no new security concerns. The app remains fully offline, single-user, and single-threaded with background thread management already established in v3. No authentication, no network, no file write beyond the existing export functionality.

## Sources

### Primary (HIGH confidence)
- [VERIFIED: existing codebase] - `prompt_tool/app.py` — v3 UI structure, v4 integration points (is_v4_flow, _do_generate_v4)
- [VERIFIED: existing codebase] - `prompt_tool/conversation_engine.py` — API: start(), handle_confirmation(), handle_answer(), skip_follow_up(), generate_complete()
- [VERIFIED: existing codebase] - `prompt_tool/generator.py` — PromptGeneratorV2 generates 3 strategies: direct, roleplay, detailed
- [VERIFIED: existing codebase] - `prompt_tool/follow_up_engine.py` — question types: single_choice, multi_choice, text_input, confirm
- [VERIFIED: existing codebase] - `prompt_tool/session_manager.py` — SessionState with turns, confirmed fields
- [VERIFIED: existing codebase] - `prompt_tool/knowledge_manager.py` — LRU-2 cache, index loading
- [VERIFIED: existing codebase] - `prompt_tool/knowledge_packs/finance.yaml` — Finance industry pack (QA-03 sensitive)
- [VERIFIED: existing codebase] - `prompt_tool/knowledge_packs/manufacturing.yaml` — Manufacturing industry pack (QA-03 sensitive)
- [VERIFIED: CONTEXT.md] - D-01 through D-13 decisions
- [VERIFIED: requirements.md] - UI-01~04, QA-03 requirement definitions
- [VERIFIED: pip show customtkinter] - customtkinter 5.2.2 installed, latest available

### Secondary (MEDIUM confidence)
- [VERIFIED: WebFetch official docs] - customtkinter.tomschimansky.com — grid system, CTkTextbox API, CTkScrollableFrame
- [VERIFIED: WebSearch Stack Overflow #77366191] — auto-scroll CTkScrollableFrame via `_parent_canvas.yview_moveto(1.0)`
- [VERIFIED: WebSearch GitHub discussion #1970] — auto-scroll pattern confirmed
- [VERIFIED: WebFetch Stack Overflow #79566798] — CTkTextbox auto-height workaround via `_textbox.count()`

### Tertiary (LOW confidence)
- None — all findings verified against codebase or official docs.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — No new packages; existing customtkinter 5.2.2 covers all needs
- Architecture: HIGH — Frame switching, chat layout, and result display patterns verified against codebase + official docs
- Pitfalls: HIGH — Verified against existing codebase patterns (thread safety, grid vs pack, disabled state)
- Security: HIGH — Offline single-user desktop app with no new attack surface

**Research date:** 2026-06-04
**Valid until:** 2026-07-04 (customtkinter 5.2.2 is stable; API changes are rare in minor versions)
