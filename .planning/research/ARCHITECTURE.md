# Architecture: Conversational Prompt Generation with Offline Knowledge Packs

**Project:** 智能提示词工坊 v4.0 (Smart Prompt Workshop)
**Researched:** 2026-06-03
**Overall confidence:** MEDIUM (all web tools unavailable; analysis based on codebase reading, established architecture patterns, and reasoned design)
**Scope:** Component structure, conversation flow, state management, data flow, knowledge integration, error handling

---

## 1. Current Architecture Analysis (v3.0)

### Current Component Diagram

```
app.py (UI)
  │
  ▼
engine.py (AnalysisEngine)
  │
  ├── knowledge.py (flat dicts: INDUSTRIES, TASK_TYPES, ROLES, ...)
  │       └── Flat per-industry maps:
  │           - keywords: str[]
  │           - templates: Dict[str, {task_keywords, description}]
  │
  └── result dict → generator.py (PromptGenerator)
          └── Template filling with 3 strategies (direct/roleplay/detailed)
```

### Current Data Flow (single turn)

```
User types text → app.py captures → engine.analyze(text)
    → keyword scoring identifies industry + task
    → returns dict with industry_key, task_name, requirements, tone, output_format
    → generator.py fills templates using result dict
    → 3 prompts displayed in tabs
```

### Problems with v3.0 Architecture

1. **No multi-turn state.** The analysis is stateless — every invocation starts from scratch. No memory of previous answers or user preferences.
2. **Knowledge is flat.** The knowledge.py dict has keywords and template names but no depth. Terms have no definitions, no relationships, no scenarios.
3. **No follow-up questions.** The system takes what it gets from the single input. It cannot ask clarifying questions (e.g., "Is this for mobile or desktop?").
4. **Intent classification is pure keyword scoring.** No confidence assessment, no ambiguity resolution, no fallback conversation.
5. **Templates are rigid.** Generator fills slots but has no awareness of the user's actual domain context or expertise level.
6. **No escalation path.** If the input is ambiguous or insufficient, the system cannot engage the user — it just produces a weaker result.
7. **Single global engine instance** (`default_engine = AnalysisEngine()`) creates subtle thread-safety issues in the UI.

---

## 2. Target Architecture (v4.0)

### High-Level Component Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  AppController (orchestrator)   │      UI (customtkinter)   │
│  SessionManager                 │      ConversationalView  │
└──────────────────────────────┬──────────────────────────────┘
                               │ events
┌──────────────────────────────▼──────────────────────────────┐
│                    CONVERSATION LAYER                        │
│  ConversationEngine (state machine)                         │
│  ├── IntentClassifier (evolved AnalysisEngine)              │
│  ├── FollowUpTreeWalker (decision tree traversal)           │
│  └── QuestionRenderer (question -> UI display format)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ context
┌──────────────────────────────▼──────────────────────────────┐
│                     CONTEXT LAYER                            │
│  ConversationContext (per-session state)                     │
│  ContextBuilder (raw context -> enriched generation input)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ knowledge
┌──────────────────────────────▼──────────────────────────────┐
│                     KNOWLEDGE LAYER                          │
│  KnowledgeManager (orchestrates packs)                       │
│  ├── KnowledgePack (per-industry structured data)           │
│  ├── KnowledgeLoader (JSON deserialization, lazy loading)  │
│  ├── KnowledgeRetriever (context-aware section selection)  │
│  └── FollowUpTreeSchema (decision tree node definitions)   │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Components | Responsibility | Depends On |
|-------|-----------|----------------|------------|
| Application | AppController, SessionManager, UI | User interaction, session lifecycle, event routing | All lower layers |
| Conversation | ConversationEngine, IntentClassifier, FollowUpTreeWalker | Multi-turn dialogue, intent analysis, question selection | Context Layer |
| Context | ConversationContext, ContextBuilder | State storage, enrichment, aggregation | Knowledge Layer |
| Knowledge | KnowledgeManager, KnowledgePack, KnowledgeRetriever | Structured domain knowledge, queries, depth management | (none — leaf layer) |

### Key Architectural Principles

1. **Strict layering.** Upper layers depend on lower layers; never the reverse. Conversation Engine calls Context, not vice versa.
2. **All state in Context.** No component holds session state internally. The ConversationEngine reads/writes to ConversationContext only.
3. **Knowledge is data, not code.** Knowledge packs are JSON files loaded at runtime. Changing knowledge never requires changing Python code.
4. **Decision trees are data.** Follow-up question trees are JSON structures. Tree traversal logic is coded once; trees vary per industry/task.
5. **Graceful degradation at every layer.** Each layer has a fallback path for when data or analysis is insufficient.

---

## 3. Component Detailed Design

### 3.1 Knowledge Layer

#### KnowledgeManager

```python
class KnowledgeManager:
    """
    Singleton that manages all loaded knowledge packs.
    - Loads a lightweight index at startup (industry names + keywords only)
    - Lazy-loads full packs on first access
    - Provides query access to all loaded packs
    """
    
    def __init__(self, packs_dir: str | Path):
        self._packs_dir = Path(packs_dir)
        self._index: dict[str, IndustryIndex] = {}  # industry_id -> {name, keywords, tasks}
        self._loaded_packs: dict[str, KnowledgePack] = {}
        self._load_index()
    
    def get_match_scores(self, text: str) -> list[tuple[str, float]]:
        """Return ranked industry matches based on keyword scoring."""
        ...
    
    def get_pack(self, industry_id: str) -> KnowledgePack:
        """Lazy-load and return a full pack."""
        if industry_id not in self._loaded_packs:
            self._loaded_packs[industry_id] = KnowledgePack(
                self._packs_dir / f"{industry_id}.json"
            )
        return self._loaded_packs[industry_id]
```

**Design rationale:** Separate index from full pack data so that industry matching is fast (only needs ~5KB per industry of keyword data). The full pack (~300KB) is loaded only for the matched industry, after the user confirms it.

#### KnowledgePack

```python
@dataclass
class KnowledgePack:
    """
    An in-memory representation of one industry's compiled knowledge.
    Wraps the raw JSON and provides typed access methods.
    Each instance is read-only after construction.
    """
    meta: PackMeta
    terms: list[Term]
    workflows: list[Workflow]
    kpis: list[KPI]
    scenarios: list[Scenario]
    follow_up_trees: list[FollowUpTree]
    templates: list[PromptTemplate]
    roles: list[IndustryRole]
    common_pitfalls: list[Pitfall]
    
    def search_terms(self, query: str) -> list[Term]: ...
    def get_follow_up_tree(self, task_key: str) -> FollowUpTree | None: ...
    def get_templates(self, task_key: str, depth: str = "standard") -> list[PromptTemplate]: ...
    def get_relevant_sections(self, context: GenerationContext) -> KnowledgeSlice: ...
```

**KnowledgeSlice** is a lightweight frozen dataclass representing only the knowledge sections relevant to the current generation task — not the full pack. This is what gets passed to the ContextBuilder.

#### KnowledgeRetriever (new component, not in v3.0)

```python
class KnowledgeRetriever:
    """
    Selects the RIGHT level of detail from a knowledge pack based on:
    - The user's confirmed task
    - The user's apparent expertise level (derived from answers)
    - The conversation context (what's already been mentioned)
    
    Three depth levels:
    - "surface": Only high-level terms and common scenarios
    - "standard": Terms + workflows + relevant KPIs (default)
    - "deep": Full details including edge cases, anti-patterns, benchmarks
    """
    
    def retrieve(self, context: ConversationContext) -> KnowledgeSlice:
        ...
```

**Why a separate retriever:** The generator should not need to know which knowledge sections to pull. The retriever makes that decision based on conversation signals (user's answers, confidence levels, stated expertise). This separation lets the retriever be optimized independently.

### 3.2 Context Layer

#### ConversationContext

The single source of truth for everything the conversation has learned about this session.

```python
@dataclass
class ConversationContext:
    """
    Per-session state object. Created fresh for each user session.
    Updated by ConversationEngine at each turn.
    Read by ContextBuilder and KnowledgeRetriever at generation time.
    """
    # --- Session identity ---
    session_id: str
    start_time: float
    
    # --- Conversation state ---
    state: ConversationState = ConversationState.IDLE
    
    # --- Original input ---
    original_input: str = ""
    cleaned_input: str = ""
    
    # --- Industry (confirmed or best-guess) ---
    suggested_industry_id: str | None = None
    suggested_industry_name: str | None = None
    suggested_industry_confidence: float = 0.0  # 0.0 - 1.0
    confirmed_industry_id: str | None = None      # Set after user confirms or corrects
    industry_confirmed: bool = False
    
    # --- Task (confirmed or best-guess) ---
    suggested_task_key: str | None = None
    suggested_task_name: str | None = None
    suggested_task_confidence: float = 0.0
    confirmed_task_key: str | None = None
    task_confirmed: bool = False
    
    # --- Gathered info from follow-up questions ---
    # Keys: "role", "scenario", "output_preference", "tone", "expertise_level", ...
    gathered_info: dict[str, Any] = field(default_factory=dict)
    
    # --- Follow-up tree position ---
    current_tree_id: str | None = None      # Which tree is active
    current_node_id: str | None = None      # Current question node
    answered_node_ids: list[str] = field(default_factory=list)
    skipped_node_ids: list[str] = field(default_factory=list)  # "I don't know"
    
    # --- User expertise signal ---
    # Derived from how many "I don't know" answers, specificity of input, jargon usage
    user_expertise: str = "unknown"  # "novice" | "intermediate" | "expert" | "unknown"
    user_uncertainty_count: int = 0
    
    # --- Conversation history ---
    turns: list[ConversationTurn] = field(default_factory=list)
    turn_count: int = 0
    
    # --- Generation state ---
    generation_context: GenerationContext | None = None
    
    # --- Error state ---
    last_error: str | None = None
```

**Why an explicit context object instead of ad-hoc state:** The current code passes loose dicts between components. This works for single-turn but breaks down at 3+ turns. An explicit dataclass gives: type safety, IDE autocomplete, single mutation surface, easy serialization (for debugging), and clear ownership.

#### ConversationTurn

```python
@dataclass
class ConversationTurn:
    role: str  # "user" | "system"
    content: str
    turn_type: str  # "input" | "question" | "answer" | "clarification" | "confirmation"
    timestamp: float
    metadata: dict = field(default_factory=dict)
```

#### GenerationContext

The enriched context built by ContextBuilder specifically for prompt generation. This is the output of the context layer and the input to the generation layer.

```python
@dataclass
class GenerationContext:
    """Built by ContextBuilder. Consumed by PromptGenerator."""
    industry_name: str
    task_name: str
    original_input: str
    user_role: str | None  # Role identified during conversation
    scenario: str | None  # Specific scenario
    requirements: list[str]
    output_format: str
    tone: str
    user_expertise: str
    knowledge_slice: KnowledgeSlice  # Relevant knowledge sections
    conversation_summary: str  # Brief text summary of what was discussed
```

### 3.3 Conversation Layer

#### ConversationEngine

This is the core orchestrator of the multi-turn dialogue. It implements a state machine governing the conversation lifecycle.

```python
class ConversationEngine:
    """
    State machine that drives the conversation flow.
    
    States:
      IDLE → INPUT_RECEIVED → ANALYZING → CLARIFYING → GENERATING → COMPLETE
                                        ↑_____________|  (loop for more questions)
    
    Events:
      - user_submits(text)
      - user_answers(question_id, answer)
      - user_restarts()
    """
    
    def __init__(self, knowledge_manager: KnowledgeManager):
        self._km = knowledge_manager
    
    def start_session(self) -> str:
        """Create new session, return session_id."""
        ...
    
    def handle_input(self, session_id: str, text: str) -> EngineResponse:
        """
        Process initial user input.
        Returns: EngineResponse with next_action (ask_question | generate | error)
        """
        context = self._get_context(session_id)
        context.state = ConversationState.ANALYZING
        
        # 1. Clean and analyze input
        classifier = IntentClassifier(self._km)
        result = classifier.analyze(text)
        
        # 2. Store analysis in context
        context.original_input = text
        context.suggested_industry_id = result.industry_id
        context.suggested_industry_confidence = result.confidence
        context.suggested_task_key = result.task_key
        
        # 3. Determine next action
        if result.confidence >= CONFIDENCE_THRESHOLD:
            # High confidence — ask for confirmation, then proceed to clarification
            return self._ask_confirmation(context, result)
        elif result.confidence >= LOW_CONFIDENCE_THRESHOLD:
            # Medium confidence — ask clarifying questions first
            return self._start_clarification(context, result)
        else:
            # Low confidence — ask basic questions to narrow down
            return self._start_basic_clarification(context, result)
    
    def handle_answer(self, session_id: str, question_id: str, answer: Any) -> EngineResponse:
        """
        Process user's answer to a follow-up question.
        Returns: EngineResponse with next_action (next_question | generate | error)
        """
        context = self._get_context(session_id)
        context.state = ConversationState.CLARIFYING
        
        # 1. Record the answer
        self._record_answer(context, question_id, answer)
        
        # 2. Walk to next node in the follow-up tree
        next_node = self._tree_walker.walk(
            tree_id=context.current_tree_id,
            current_node_id=question_id,
            answer=answer,
            context=context
        )
        
        if next_node is None:
            # No more questions — time to generate
            return self._proceed_to_generation(context)
        elif next_node.question_type == QuestionType.LEAF:
            # Leaf node signals end of this tree
            return self._proceed_to_generation(context)
        else:
            # More questions to ask
            context.current_node_id = next_node.node_id
            return EngineResponse(
                action=Action.ASK_QUESTION,
                question=next_node,
                state=context.state
            )
```

**Why a state machine?** The conversation has clear, well-defined states with predictable transitions. A state machine:
- Makes the flow explicit and auditable
- Prevents invalid transitions (e.g., cannot go from IDLE to GENERATING)
- Makes it obvious where to add new states later (e.g., REVIEW for user preview)
- Enables testing of individual state transitions

#### IntentClassifier (evolved from AnalysisEngine)

The current `engine.py` does flat keyword scoring. The v4.0 classifier wraps this same logic but adds:

1. **Confidence scoring** — Not just the top match, but the margin between #1 and #2
2. **Ambiguity detection** — If two industries have close scores, flag as ambiguous
3. **Fallback routing** — If confidence < threshold, route to clarification flow
4. **Knowledge pack index matching** — Uses KnowledgeManager's index instead of importing knowledge.py

```python
class IntentClassifier:
    """
    Evolved from v3.0 AnalysisEngine.
    Same keyword matching logic but:
    - Returns confidence scores (not just best match)
    - Routes ambiguous results to conversation flow
    - Uses KnowledgeManager index (not raw knowledge.py dicts)
    """
    
    def analyze(self, text: str) -> AnalysisResult:
        """
        Returns structured result with confidence metrics.
        
        AnalysisResult:
          industry_id: str
          industry_name: str
          industry_confidence: float
          task_key: str
          task_name: str
          task_confidence: float
          requirements: list[str]
          tone: str
          output_format: str
          all_industry_scores: list[tuple[str, float]]
          is_ambiguous: bool
        """
```

**Why reuse keyword matching?** The v3.0 keyword matching works and is already tuned for 16 industries. Rewriting it would be wasted effort. The improvement is in the CONVERSATION FLOW around it, not the matching algorithm itself.

#### FollowUpTreeWalker

This is the component that traverses the 追问逻辑树 (follow-up question logic tree).

```python
class FollowUpTreeWalker:
    """
    Walks the decision tree defined by a FollowUpTree JSON structure.
    
    The tree is defined as a directed acyclic graph of QuestionNodes:
    
    QuestionNode:
      node_id: str
      question_text: str
      question_type: "single_choice" | "multi_choice" | "text_input" | "confirm"
      options: list[Option]  # for choice types
      info_key: str           # where to store in context.gathered_info
      children: dict[str, str]  # {option_value -> next_node_id}
      fallback_node_id: str | None  # "I don't know" / "none of the above" path
      is_leaf: bool
      depth: int              # How deep in the tree
    """
    
    def walk(
        self,
        tree: FollowUpTree,
        current_node_id: str,
        answer: Any,
        context: ConversationContext
    ) -> QuestionNode | None:
        """
        Given the current node and user's answer, find the next node.
        Returns None if the tree is complete (leaf reached).
        """
        node = tree.get_node(current_node_id)
        
        if node.is_leaf:
            return None
        
        # Determine which child path to follow
        next_id = self._resolve_next(node, answer, context)
        
        if next_id is None:
            return None  # Tree complete
        
        return tree.get_node(next_id)
    
    def _resolve_next(
        self, node: QuestionNode, answer: Any, context: ConversationContext
    ) -> str | None:
        """Determine next node based on answer type."""
        
        if answer_is_dont_know(answer):
            context.user_uncertainty_count += 1
            context.skipped_node_ids.append(node.node_id)
            if node.fallback_node_id:
                return node.fallback_node_id
            # No fallback — try to skip this question
            return self._find_next_after_skip(node)
        
        if node.question_type == "single_choice":
            return node.children.get(str(answer))
        elif node.question_type == "multi_choice":
            # Multi-choice follows the HIGHEST-PRIORITY selected path
            selected = parse_multi_choice(answer)
            for choice in selected:
                if choice in node.children:
                    return node.children[choice]
            return node.fallback_node_id
        elif node.question_type == "text_input":
            # Text answers use a catch-all child or fallback
            return node.children.get("_any", node.fallback_node_id)
        elif node.question_type == "confirm":
            return node.children.get(str(answer).lower())
        
        return node.fallback_node_id
    
    def _find_next_after_skip(self, node: QuestionNode) -> str | None:
        """When a question has no fallback, find the next question at same or parent depth."""
        # Logic: skip this node, try parent's next sibling, or go up one level
        ...
```

**Why a decision tree (not a pure state machine or rule engine) for follow-up questions?**

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Decision tree (DAG)** | Natural for branching logic; easy to define as JSON; traversable; testable; visualizable | Less flexible for complex conditions | BEST FIT — the conversation IS a tree of questions |
| **Pure state machine** | Formal semantics; well-understood | Every question branch needs explicit states; explodes combinatorially | Wrong abstraction — too low-level |
| **Rule engine** | Flexible; declarative | Overkill for this scale; hard to trace flow; slow for offline | Over-engineered |
| **Scripted flow** (if/else in code) | Simple; no data format | Not data-driven; changes require code release; domain experts can't edit | Current approach; exactly what we're replacing |
| **Behavior tree** (gamedev pattern) | Supports sequences, selectors, conditions | Unfamiliar to non-gamedev team; more complex than needed | Interesting but unnecessary |

The decision tree is the right fit because:
- Each question naturally has a finite set of answer branches
- The tree structure maps directly to user comprehension ("if you say X, I'll ask about Y")
- Trees can be defined as data (JSON in the knowledge pack) and edited by domain experts
- Trees support "I don't know" via fallback branches
- Depth levels map naturally to novice/intermediate/expert flows

### 3.4 Application Layer

#### AppController

The AppController bridges the asynchronous UI (customtkinter) with the synchronous ConversationEngine. It handles threading, state synchronization, and event routing.

```python
class AppController:
    """
    Mediates between UI and backend components.
    Runs blocking operations in background threads.
    Manages session lifecycle.
    """
    
    def __init__(self, engine: ConversationEngine):
        self._engine = engine
        self._session_id: str | None = None
    
    def start_new_session(self):
        self._session_id = self._engine.start_session()
    
    def process_input(self, text: str) -> None:
        """Called by UI when user submits input. Runs in thread."""
        response = self._engine.handle_input(self._session_id, text)
        self._apply_response(response)
    
    def process_answer(self, question_id: str, answer: Any) -> None:
        """Called by UI when user answers a question. Runs in thread."""
        response = self._engine.handle_answer(self._session_id, question_id, answer)
        self._apply_response(response)
    
    def _apply_response(self, response: EngineResponse):
        """Update UI based on engine response."""
        if response.action == Action.ASK_QUESTION:
            # Tell UI to display a question widget
            ...
        elif response.action == Action.CONFIRM:
            # Tell UI to show confirmation
            ...
        elif response.action == Action.GENERATE:
            # Tell UI to show generation progress, then result
            ...
```

---

## 4. Conversation State Machine Detail

### State Definitions

```python
class ConversationState(enum.Enum):
    IDLE = "idle"                    # No session active, waiting
    INPUT_RECEIVED = "input_received"  # User submitted initial text
    ANALYZING = "analyzing"          # Engine processing input
    NEEDS_CLARIFICATION = "needs_clarification"  # Ambiguous, needs confirmation
    CLARIFYING = "clarifying"        # Asking follow-up questions (may loop)
    CONFIRMING = "confirming"        # Asking user to confirm something
    GENERATING = "generating"        # Building final prompt
    COMPLETE = "complete"            # Prompt displayed, waiting for user action
    ERROR = "error"                  # Recoverable error
    FAILED = "failed"                # Unrecoverable error
```

### State Transition Diagram

```
                          ┌─────────────────────────────────────┐
                          │                                     │
                          ▼                                     │
    IDLE ──input──► INPUT_RECEIVED                              │
                      │                                         │
                      ▼                                         │
                  ANALYZING                                     │
                   │      │                                     │
          ┌────────┘      └────────────┐                       │
          ▼                            ▼                        │
    (high conf)                 (low/med conf)                  │
          │                            │                        │
          ▼                            ▼                        │
    CONFIRMING              NEEDS_CLARIFICATION                 │
          │                      │     │                        │
    ┌─────┼─────┐          ┌─────┘     └─────┐                 │
    ▼     ▼     ▼          ▼                   ▼                │
  correct wrong unsure  CLARIFYING          BASIC_CLARIFYING    │
    │     │     │          │                   │                │
    │     └──┬──┘          │ ──answer──► re-evaluate ──┐        │
    │        │             │                           │        │
    ▼        ▼             │◄──────────────────────────┘        │
  proceed  re-analyze      │                                    │
    │        │             │ (if still ambiguous)               │
    └───┬────┘             │                                    │
        │                  ▼                                    │
        ▼              GENERATING                               │
        │                  │                                    │
        ▼                  ▼                                    │
    CLARIFYING          COMPLETE ──restart──► (back to IDLE)   │
        │                  │                                    │
        │                  ▼                                    │
        │                (user copies/export)                   │
        │                  │                                    │
        └──────────────────┘ (or back to clarifying)            │
                           │                                    │
                           └────────────────────────────────────┘
```

### Transition Rules

| From | Event | To | Condition |
|------|-------|----|-----------|
| IDLE | `start_session()` | INPUT_RECEIVED | Always |
| INPUT_RECEIVED | input submitted | ANALYZING | Text non-empty |
| ANALYZING | analysis complete | CONFIRMING | Confidence > 0.7 |
| ANALYZING | analysis complete | NEEDS_CLARIFICATION | 0.3 <= Confidence <= 0.7 |
| ANALYZING | analysis complete | CLARIFYING | Confidence < 0.3, needs basic info |
| CONFIRMING | user says "correct" | CLARIFYING | Industry/task confirmed |
| CONFIRMING | user says "wrong" | ANALYZING | Re-analyze with corrected info |
| CONFIRMING | user says "unsure" | CLARIFYING | Accept best guess, proceed |
| CLARIFYING | answer received | CLARIFYING | More questions remain |
| CLARIFYING | answer received | GENERATING | All required info gathered |
| GENERATING | generation complete | COMPLETE | Prompt ready |
| COMPLETE | user restarts | IDLE | Session reset |
| ANY | exception caught | ERROR | Recoverable |
| ERROR | retry | previous state | User clicks retry |
| ANY | fatal error | FAILED | Unrecoverable |

---

## 5. Follow-Up Question Logic Tree (追问逻辑树) Design

### Tree Structure

Each knowledge pack contains a `follow_up_trees` section with one tree per task type. The tree is organized hierarchically:

```
Industry: 互联网/IT
  Task: 代码生成
    Level 1 (surface, always asked):
      Q1: "你想生成什么类型的代码？"
        - 后端API        → Q2a
        - 前端页面        → Q2b
        - 数据处理脚本    → Q2c
        - 其他/不确定    → Q1_fallback
      
    Level 2 (task-specific detail):
      Q2a (for 后端API):
        "使用什么语言/框架？"
        - Python/Flask   → Q3a
        - Java/Spring    → Q3b
        - Node.js/Express → Q3c
        - 不确定          → Q2a_fallback
      
      Q2b (for 前端页面):
        "是PC端还是移动端？"
        - PC端           → Q3d
        - 移动端/H5      → Q3e
        - 小程序         → Q3f
        - 不确定          → Q2b_fallback
    
    Level 3 (depth depends on user expertise):
      If user_expertise == "novice":
        Q_final: "你希望输出包含什么？"
          - 完整代码+注释
          - 核心代码片段
          - 代码+使用说明
      
      If user_expertise == "expert":
        Q_final: "有什么特殊需求？(性能要求/安全考量/部署环境)"
          - (free text input)
```

### JSON Representation

```json
{
  "follow_up_trees": [
    {
      "task_type": "代码生成",
      "root_node_id": "q1",
      "nodes": {
        "q1": {
          "question_text": "你想生成什么类型的代码？",
          "question_type": "single_choice",
          "info_key": "code_type",
          "depth": 1,
          "options": [
            {"value": "backend_api", "label": "后端API"},
            {"value": "frontend", "label": "前端页面"},
            {"value": "data_script", "label": "数据处理脚本"},
            {"value": "other", "label": "其他"}
          ],
          "children": {
            "backend_api": "q2_backend",
            "frontend": "q2_frontend",
            "data_script": "q2_data",
            "other": "q2_generic"
          },
          "fallback_node_id": "q1_fallback"
        },
        "q1_fallback": {
          "question_text": "没关系，能简单描述一下你想做什么吗？比如是做网站、写工具、还是处理数据？",
          "question_type": "single_choice",
          "info_key": "code_type_simple",
          "depth": 1,
          "options": [
            {"value": "web", "label": "网站/Web应用"},
            {"value": "tool", "label": "工具脚本"},
            {"value": "data", "label": "数据处理"},
            {"value": "general", "label": "其他编程任务"}
          ],
          "children": {
            "web": "q2_web_simple",
            "tool": "q2_tool_simple",
            "data": "q2_data",
            "general": "q2_generic"
          },
          "fallback_node_id": "q2_generic"
        },
        "q2_backend": {
          "question_text": "使用什么语言/框架？",
          "question_type": "single_choice",
          "info_key": "language",
          "depth": 2,
          "options": [
            {"value": "python", "label": "Python (Flask/FastAPI/Django)"},
            {"value": "java", "label": "Java (Spring Boot)"},
            {"value": "node", "label": "Node.js (Express/Nest)"},
            {"value": "go", "label": "Go"},
            {"value": "other", "label": "其他"}
          ],
          "children": {
            "python": "q3_python_backend",
            "java": "q3_java_backend",
            "node": "q3_node_backend",
            "go": "q3_go_backend",
            "other": "q3_generic_backend"
          },
          "fallback_node_id": "q3_generic_backend"
        },
        "q3_python_backend": {
          "question_text": "这个后端主要实现什么功能？",
          "question_type": "multi_choice",
          "info_key": "backend_features",
          "depth": 3,
          "options": [
            {"value": "crud", "label": "增删改查 (CRUD)"},
            {"value": "auth", "label": "用户认证/权限"},
            {"value": "api", "label": "RESTful API接口"},
            {"value": "file", "label": "文件上传/下载"},
            {"value": "data_sync", "label": "数据同步/定时任务"}
          ],
          "children": {
            "crud": "q4_output",
            "auth": "q4_output",
            "api": "q4_output",
            "file": "q4_output",
            "data_sync": "q4_output"
          },
          "fallback_node_id": "q4_output",
          "is_leaf": false
        },
        "q4_output": {
          "question_text": "你希望输出包含哪些内容？",
          "question_type": "multi_choice",
          "info_key": "output_requirements",
          "depth": 4,
          "options": [
            {"value": "full_code", "label": "完整可运行的代码"},
            {"value": "comments", "label": "详细注释说明"},
            {"value": "error_handling", "label": "异常处理和边界情况"},
            {"value": "tests", "label": "单元测试"},
            {"value": "docs", "label": "使用文档/README"}
          ],
          "children": {},
          "fallback_node_id": null,
          "is_leaf": true
        }
      }
    }
  ]
}
```

### Depth Categories

| Depth Level | When Reached | Question Style | Knowledge Used |
|-------------|-------------|----------------|----------------|
| 1 (Surface) | Always asked | Broad categories, simple choices | Task identification only |
| 2 (Standard) | After basic choice | Specific details (language, platform, role) | Workflows, common scenarios |
| 3 (Detailed) | After standard questions | Technical depth, edge cases | KPIs, benchmarks, anti-patterns |
| 4 (Expert) | User shows expertise | Advanced options, tradeoffs | Edge cases, optimization, expert patterns |

### "I Don't Know" / "None of the Above" Handling Strategy

The system handles uncertainty at three levels:

**Level 1: Per-node fallback.** Every question has a `fallback_node_id`. When the user selects "不确定" or "其他", the walker routes to the fallback question, which is:
- Simpler (fewer options, broader categories)
- More descriptive (longer explanation of each option)
- Less technical language

**Level 2: Progressive simplification.** If the user hits fallbacks repeatedly (tracked via `user_uncertainty_count`), the system progressively simplifies:
- After 2 uncertainty answers: Switch to "simple" mode — use plain language, 2-3 broad options
- After 4 uncertainty answers: Switch to "guided" mode — provide examples and ask "which sounds closest?"
- At any point, user can type free text instead of selecting

**Level 3: Graceful degradation.** If uncertainty is too high:
- Skip remaining task-specific questions and go to generic fallback tree
- Mark the user's expertise as "novice" in context
- Generate with broader, more educational prompts
- Add explanatory notes to the generated prompt

**Implementation in code:**

```python
class UncertaintyHandler:
    """Handles user uncertainty during conversation."""
    
    SIMPLIFICATION_THRESHOLD_1 = 2   # After 2 "I don't know" -> simplify
    SIMPLIFICATION_THRESHOLD_2 = 4   # After 4 -> guided mode
    
    def handle_dont_know(
        self,
        node: QuestionNode,
        context: ConversationContext
    ) -> QuestionNode:
        context.user_uncertainty_count += 1
        
        # Level 1: Use per-node fallback
        if node.fallback_node_id:
            return self._tree.get_node(node.fallback_node_id)
        
        # Level 2: Progressive simplification
        if context.user_uncertainty_count >= self.SIMPLIFICATION_THRESHOLD_2:
            return self._get_guided_fallback(node, context)
        elif context.user_uncertainty_count >= self.SIMPLIFICATION_THRESHOLD_1:
            return self._get_simplified_fallback(node, context)
        
        # Level 3: Skip this question
        return self._skip_question(node, context)
    
    def _get_simplified_fallback(self, node: QuestionNode, context: ConversationContext) -> QuestionNode:
        """Replace technical options with plain-language categories."""
        # Use the tree's built-in simplified fallback path
        simplified_tree_id = f"{self._tree.tree_id}_simplified"
        simplified = self._tree.get_node(f"{node.node_id}_simple")
        if simplified:
            return simplified
        # Or skip if no simplified version
        return self._skip_question(node, context)
    
    def _get_guided_fallback(self, node: QuestionNode, context: ConversationContext) -> QuestionNode:
        """Provide examples and ask 'which sounds closest?'"""
        # Look for optional "guided_mode" alternative on this node
        guided = self._tree.get_node(f"{node.node_id}_guided")
        if guided:
            return guided
        # Fall back to text input prompt
        return TextInputNode(
            node_id=f"{node.node_id}_text",
            question_text="你可以自由描述你的需求，我会尽力理解并给出最好的提示词。"
        )
    
    def _skip_question(self, node: QuestionNode, context: ConversationContext) -> QuestionNode | None:
        """Skip this question entirely and find the next unasked question."""
        context.skipped_node_ids.append(node.node_id)
        next_node = self._find_next_node_at_same_level(node)
        if next_node:
            return next_node
        # No more questions at this level — move to generation
        return None
```

---

## 6. Data Flow: User Input to Generated Prompt

### Complete Flow Sequence

```
Step 1: USER INPUT
────────────
User types: "帮我写一个管理后台的代码"
UI triggers: controller.process_input(text)

Step 2: ANALYSIS
────────────
ConversationEngine.handle_input() called
  ├── IntentClassifier.analyze(text)
  │     ├── KnowledgeManager.get_match_scores(text) → [("互联网_IT", 0.85), ...]
  │     ├── Identify task: "代码生成"
  │     └── Return AnalysisResult(industry="互联网_IT", conf=0.85, task="代码生成", ...)
  │
  ├── ConversationContext updated:
  │     suggested_industry_id = "互联网_IT"
  │     suggested_industry_confidence = 0.85
  │     suggested_task_key = "代码生成"
  │
  └── Decision: confidence 0.85 > 0.7 threshold → CONFIRMING state
        → Return: EngineResponse(action=CONFIRM, question="您是互联网/IT行业的吗？")

Step 3: CONFIRMATION (if needed)
────────────
UI shows: "我理解的是『互联网/IT行业』，对吗？ [是] [不是] [不确定]"
User clicks: "是"
  ├── context.confirmed_industry_id = "互联网_IT"
  ├── context.industry_confirmed = True
  └── Transition to CLARIFYING state

Step 4: TASK CONFIRMATION
────────────
Engine: "你是要『代码生成』相关的任务，对吗？ [是] [不是，我是要...]"
User clicks: "是"
  ├── context.confirmed_task_key = "代码生成"
  ├── context.task_confirmed = True
  └── KnowledgeManager.get_pack("互联网_IT") → lazy loads full pack

Step 5: FOLLOW-UP QUESTIONS
────────────
KnowledgePack.get_follow_up_tree("代码生成") → returns tree
FollowUpTreeWalker starts at root_node "q1"

Turn 1: "你想生成什么类型的代码？"
  → User: "后端API"
  → context.gathered_info["code_type"] = "backend_api"
  → Walker moves to "q2_backend"

Turn 2: "使用什么语言/框架？"
  → User: "Python (Flask/FastAPI/Django)"
  → context.gathered_info["language"] = "python"
  → Walker moves to "q3_python_backend"

Turn 3: "这个后端主要实现什么功能？"
  → User: "增删改查 + 用户认证"
  → context.gathered_info["backend_features"] = ["crud", "auth"]
  → Walker moves to "q4_output"

Turn 4: "你希望输出包含哪些内容？"
  → User: "完整可运行的代码 + 详细注释"
  → context.gathered_info["output_requirements"] = ["full_code", "comments"]
  → Walker: is_leaf → return None
  → No more questions → transition to GENERATING

Step 6: CONTEXT BUILDING
────────────
ContextBuilder.build(context) → GenerationContext
  ├── Copies: industry, task, original_input, gathered_info
  ├── Derives: user_expertise from uncertainty_count (0 → "intermediate" default)
  ├── Calls: KnowledgeRetriever.retrieve(context) → KnowledgeSlice
  │     └── Filters pack for: code_gen_terms, python_backend_workflows, api_best_practices
  └── Returns complete GenerationContext

Step 7: PROMPT GENERATION
────────────
PromptGenerator.generate(context=GenerationContext)
  ├── Strategy selection:
  │     If user is novice → prefer "详细式" (detailed)
  │     If user typed specific jargon → consider "直给式" (direct)
  │     Default → generate based on user preference (or offer all 3 as v3.0 does)
  │
  ├── Knowledge injection:
  │     - Role description includes domain depth
  │     - Requirements include domain-specific quality criteria
  │     - Output format hints include industry-standard structure
  │
  ├── Template filling:
  │     Uses templates from KnowledgePack (not hardcoded)
  │     Injects knowledge_slice.terms, .workflows, .best_practices
  │
  └── Returns: prompt text

Step 8: DISPLAY
────────────
UI shows: generated_prompt + copy/export buttons
  ├── ConversationEngine state → COMPLETE
  ├── User can restart or export
  └── Option to go back and change answers
```

### Simplified Flow Diagram (for quick reference)

```
User Input
    │
    ▼
IntentClassifier ──low conf──► Basic Questions ──answer──► (loop)
    │
    ▲ high conf                    │
    │    │                         │ enough?
    │    ▼                         │
    │ Confirm Industry/Task ──wrong──► Re-analyze
    │    │                         │
    │    ▼ correct/unsure          │
    │    │                         │
    │    ▼                         │
    │ Follow-Up Tree ──question──► User Answer
    │    │                         │
    │    │◄───────(loop)────────────┘
    │    │
    │    ▼ leaf reached
    │    │
    │    ▼
    ContextBuilder → KnowledgeRetriever
    │
    ▼
    PromptGenerator → Generated Prompt
```

---

## 7. Knowledge Pack Integration in Prompt Generation

### How Knowledge Feeds Into Generation

The generator doesn't just fill templates. It uses knowledge from the pack at four integration points:

**Integration Point 1: Role Depth**

```
Before (v3.0):  "你是一位资深互联网产品与技术专家"
After  (v4.0):  "你是一位资深的互联网/IT行业专家，精通Python后端开发、
                 熟悉FastAPI和Django框架，对RESTful API设计、用户认证、
                 数据库设计和性能优化有丰富经验。"
```

The role description is built dynamically from:
- Industry + task identity
- Confirmed language/framework (from gathered_info)
- Relevant terms from knowledge pack (expertise description)
- User expertise level (add more/less detail)

**Integration Point 2: Quality Criteria**

```
Before (v3.0):  "- 代码完整可运行，添加必要注释\n- 考虑异常处理和边界情况"
After  (v4.0):  "- 代码完整可运行，使用FastAPI框架，添加路由、依赖注入和中间件\n
                  - 实现JWT用户认证中间件，包含token刷新机制\n
                  - 数据库操作使用SQLAlchemy ORM，包含事务处理和连接池配置\n
                  - API响应遵循RESTful规范，包含统一错误格式和状态码\n
                  - 添加日志记录：请求日志、错误日志、性能日志\n
                  - 考虑并发安全：使用async/await处理IO操作"
```

The criteria are generated by looking up relevant terms (FastAPI, JWT, SQLAlchemy, RESTful) from the knowledge pack's code_gen task sections.

**Integration Point 3: Output Structure**

```
Before (v3.0):  "请以清晰的分段文字输出，重要内容可用列表呈现"
After  (v4.0):  "请按以下结构输出：
                  1. 项目结构和文件清单
                  2. 核心代码（按模块分节）
                  3. 数据库模型定义
                  4. API路由和端点
                  5. 配置和部署说明
                  6. 依赖和安装步骤"
```

The output structure comes from the knowledge pack's template for the task.

**Integration Point 4: Anti-Pattern Warnings**

```
v4.0 (new):  "注意事项：
              - 避免在路由处理函数中直接操作数据库（应使用Service层）
              - JWT密钥不要硬编码在代码中
              - API版本号应在URL中体现（/api/v1/...）
              - 密码存储必须使用哈希（如bcrypt），不得明文存储"
```

Anti-patterns are extracted from the knowledge pack's `common_pitfalls` section that match the current task and context.

### Depth Filtering Algorithm

```python
class KnowledgeRetriever:
    
    def _determine_depth(self, context: ConversationContext) -> str:
        """Decide which knowledge depth to provide based on user signals."""
        
        # Explicit depth from user
        if context.gathered_info.get("expertise_level") == "beginner":
            return "surface"
        if context.gathered_info.get("expertise_level") == "advanced":
            return "deep"
        
        # Implicit depth from behavior
        high_uncertainty = context.user_uncertainty_count >= 3
        used_jargon = self._detect_jargon(context.original_input, context.confirmed_industry_id)
        
        if high_uncertainty:
            return "surface"
        if used_jargon:
            return "deep"
        
        return "standard"
    
    def _select_sections(self, pack: KnowledgePack, depth: str, task_key: str) -> KnowledgeSlice:
        """Select which sections of the knowledge pack to include."""
        all_terms = pack.get_terms(depth=depth, task=task_key)
        all_workflows = pack.get_workflows(depth=depth, task=task_key)
        all_kpis = pack.get_kpis(depth=depth, task=task_key) if depth in ("standard", "deep") else []
        all_pitfalls = pack.get_pitfalls(task=task_key) if depth == "deep" else []
        
        return KnowledgeSlice(
            terms=all_terms,
            workflows=all_workflows,
            kpis=all_kpis,
            pitfalls=all_pitfalls,
            depth=depth
        )
```

---

## 8. Thread Safety and Session Isolation

### Problem in v3.0

The current code uses a global `default_engine = AnalysisEngine()` imported at module level. This engine is not thread-safe -- its `industry_scores` and `task_scores` attributes are overwritten by each `analyze()` call. In a threaded UI (v3.0 already uses `threading.Thread` for generation), this is a race condition.

### Solution in v4.0

1. **No global state.** Each session gets its own ConversationEngine session (backed by a ConversationContext).
2. **KnowledgeManager is read-only** after construction. Multiple sessions can share the same manager safely.
3. **Session store** in AppController maps session_id -> context:

```python
class SessionManager:
    """Thread-safe session management."""
    
    def __init__(self):
        self._sessions: dict[str, ConversationContext] = {}
        self._lock = threading.Lock()
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        with self._lock:
            self._sessions[session_id] = ConversationContext(
                session_id=session_id,
                start_time=time.time()
            )
        return session_id
    
    def get_context(self, session_id: str) -> ConversationContext | None:
        with self._lock:
            return self._sessions.get(session_id)
    
    def update_context(self, session_id: str, **updates) -> bool:
        with self._lock:
            ctx = self._sessions.get(session_id)
            if not ctx:
                return False
            for k, v in updates.items():
                setattr(ctx, k, v)
            return True
```

---

## 9. Error Handling Strategy

### Per-Component Error Boundaries

| Component | Error Scenario | Handling |
|-----------|---------------|----------|
| KnowledgeLoader | JSON file missing/malformed | Log error, fall back to embedded fallback pack (compiled into Python as last resort) |
| KnowledgeLoader | Knowledge pack not found for industry | Use generic pack |
| IntentClassifier | No industry match | Return lowest confidence, route to CLARIFYING |
| FollowUpTreeWalker | Tree node not found | Skip question, go to next sibling |
| FollowUpTreeWalker | Circular reference in tree | Depth limit (max 20), break loop |
| ConversationEngine | Invalid state transition | Log, reset to ANALYZING |
| PromptGenerator | Template variable missing | Use default text, don't crash |
| PromptGenerator | Generation timeout (>2s) | Return best-effort result, log timeout |

### Graceful Degradation Chain

```
Full generation with deep knowledge
    ↓ (if knowledge pack missing)
Generation with generic knowledge
    ↓ (if follow-up tree missing)
Keyword-based generation (v3.0 fallback)
    ↓ (if conversation engine fails)
Direct template filling with user's original input
```

This chain ensures the tool always produces SOMETHING, even if the knowledge packs or conversation system fail.

---

## 10. Build Order and Dependencies

### Phase Structure Rationale

The architecture has clear dependency ordering:

```
Phase 1: Foundation
  ├── Knowledge pack schema (data model)
  ├── Follow-up tree schema
  └── Knowledge pack for 1 test industry
  
Phase 2: Knowledge Layer
  ├── KnowledgeLoader (JSON loading)
  ├── KnowledgePack (typed access)
  └── KnowledgeManager (index + lazy load)

Phase 3: Context Layer  
  ├── ConversationContext dataclass
  ├── ConversationTurn dataclass
  └── SessionManager

Phase 4: Conversation Core
  ├── IntentClassifier (wrap existing AnalysisEngine)
  ├── FollowUpTreeWalker
  ├── UncertaintyHandler
  └── ConversationEngine (state machine)

Phase 5: Generation
  ├── KnowledgeRetriever
  ├── ContextBuilder
  ├── PromptGenerator v2 (uses context + knowledge instead of flat template)
  └── 3 strategies updated

Phase 6: UI
  ├── ConversationalView (multi-turn question display)
  └── AppController (bridges UI with engine)

Phase 7: Scale
  ├── Knowledge packs for remaining 4 core industries
  ├── Follow-up trees for remaining industries
  └── Content quality review
```

### Why This Order

1. **Phase 1 first** because the data schema defines the contracts everything else depends on. Without knowing what a knowledge pack looks like, you cannot write the loader, the retriever, or the generator.
2. **Phase 2 before Phase 3** because ConversationContext holds a reference to KnowledgePack. Context depends on knowing what knowledge exists.
3. **Phase 3 before Phase 4** because the ConversationEngine reads and writes ConversationContext. The context must exist before the engine can use it.
4. **Phase 5 before Phase 6** because the UI needs something to display. Generation logic must work before the conversation UI can be built.
5. **Phase 7 last** because scaling knowledge packs is content work, not architecture work. The architecture should be validated with one industry before expanding.

---

## 11. Key Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Conversation orchestration | State machine | Clear states, explicit transitions, prevent invalid flows |
| Follow-up question logic | Decision tree (DAG) as JSON | Data-driven, domain-editable, testable, maps naturally to conversation |
| State storage | Single ConversationContext dataclass | Type-safe, single mutation surface, serializable |
| Thread safety | SessionManager with lock, no global state | Fixes v3.0 race condition |
| Knowledge integration | 4 injection points (role, criteria, structure, anti-patterns) | Depth-appropriate knowledge without overloading templates |
| Depth selection | Automatic via user signals | No manual depth setting needed |
| Uncertainty handling | 3-level progressive simplification | Maintains usability without frustrating users |
| Fallback chain | 4-level degradation | Always produces output |
| Session isolation | Per-session context | Supports multiple concurrent sessions (future) |
| Lazy loading | Index first, full pack on match | Fast startup (~5ms), ~300KB per pack loaded on demand |

---

## 12. Files Affected by Architecture Change

| Current File | Status in v4.0 | Notes |
|-------------|----------------|-------|
| `prompt_tool/knowledge.py` | **Removed** | Replaced by knowledge_packs/ JSON files + KnowledgeManager |
| `prompt_tool/engine.py` | **Rewritten** | v4.0 IntentClassifier wraps existing logic + confidence scoring |
| `prompt_tool/generator.py` | **Rewritten** | v4.0 PromptGenerator uses context + knowledge slice instead of flat dict |
| `prompt_tool/app.py` | **Significantly extended** | Conversational UI + AppController + threading |
| (new) `knowledge_manager.py` | **New** | Loads/validates/accesses knowledge packs |
| (new) `knowledge_pack.py` | **New** | KnowledgePack typed dataclass |
| (new) `knowledge_retriever.py` | **New** | Depth-aware knowledge selection |
| (new) `conversation_engine.py` | **New** | State machine + orchestration |
| (new) `follow_up_tree.py` | **New** | Decision tree walker + question nodes |
| (new) `context.py` | **New** | ConversationContext, GenerationContext, ConversationTurn |
| (new) `context_builder.py` | **New** | Enriches context for generation |
| (new) `session_manager.py` | **New** | Thread-safe session store |
| (new) `app_controller.py` | **New** | Mediates UI ↔ engine |
| (new) `knowledge_packs/*.yaml` | **New** | YAML source files for authoring |
| (new) `knowledge_packs_compiled/*.json` | **New** | Compiled JSON for runtime |

---

## 13. Open Questions and Risks

### Open Questions (Need Deeper Research)

1. **What is the maximum practical depth of the follow-up tree before users abandon?** If more than 5-6 questions, users may get impatient. Need to test with real users to find the sweet spot.

2. **How do we handle partial session resumption?** If the user closes and reopens the app, should we resume where they left off? This conflicts with the "single file exe, no persistent storage" constraint. A lightweight JSON save to a temp directory might work.

3. **How does the uncertainty detection perform with Chinese text?** The "used jargon" heuristic needs to be tuned per industry. Not all industry terms are equally recognizable.

4. **Do all 5 core industries need uniquely designed follow-up trees, or can some share a template?** Sales/retail and manufacturing might share generic "create a plan" trees. Need content analysis.

### Architectural Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Trees too deep → user abandonment | Conversation fails | Cap at 5 questions max per tree; allow early exit to generation |
| Knowledge pack data stale | Outdated recommendations | Version field in meta; rebuild pipeline can regenerate quarterly |
| Decision tree data grows complex | Hard to maintain | Schema validation at build time; tree visualization tool |
| Performance with 5+ industries | Startup > 2s | Lazy loading ensures < 50ms startup |
| Thread safety regression from v3.0 | Race conditions | SessionManager lock; no global state |
| Chinese text matching in JMESPath | Missed matches | Python fallback for fuzzy/contains queries |
