# Project Research Summary

**Project:** 智能提示词工坊 (Smart Prompt Workshop) v4.0
**Domain:** Offline desktop prompt generation tool with embedded industry knowledge packs
**Researched:** 2026-06-03
**Confidence:** MEDIUM

## Executive Summary

**This product is an offline desktop tool that generates deep, industry-specific prompts by combining structured knowledge packs with a multi-turn conversational requirements mining flow.** Unlike web-based prompt template libraries (AIPRM, PromptBase) or generic ChatGPT interactions, this tool targets users who need prompts that sound like an industry insider -- product managers writing PRDs, factory engineers writing 8D reports, or teachers writing lesson plans -- all running 100% offline as a single Windows executable.

**The recommended approach is a two-format knowledge pipeline (YAML authoring -> JSON runtime) paired with a state machine-driven conversational engine that clarifies user intent through structured question trees.**

**The three most critical risks are: (1) the Template Trap, (2) Dialogue Fatigue, and (3) PyInstaller packaging bloat.**

## Key Findings

### Recommended Stack
YAML-to-JSON compile pipeline with JMESPath for structured queries and Python dataclasses for typed access. YAML for authoring (supports comments, multi-line strings, anchors). JSON for runtime (stdlib, 3-5x faster loading, zero extra dependency). Pydantic v2 for build-time validation only.

- **YAML 1.2 (PyYAML)**: Knowledge pack authoring format
- **JSON (stdlib)**: Runtime data format
- **JMESPath 1.x**: Structured query language for knowledge pack lookups
- **Python dataclasses**: Typed access layer
- **Pydantic v2** (dev-time only): Schema validation
- **No additional runtime dependencies** beyond existing customtkinter + Pillow + jmespath

### Expected Features
8 content dimensions per industry knowledge pack: Industry Fundamentals, Terminology Dictionary (3-level), Common Task Scenarios (10-15 per industry), Role Knowledge, Document Standards, Core Processes, Pain Points & Pitfalls, and 追问逻辑树 (follow-up question trees).

### Architecture Approach
Four-layer architecture: Knowledge Layer -> Context Layer -> Conversation Layer -> Application Layer.
- **KnowledgeManager + KnowledgePack**: Lazy-loads packs (~300 KB each)
- **ConversationEngine (state machine)**: 9 states, multi-turn dialogue
- **IntentClassifier**: Confidence scoring, rejection-based classification
- **FollowUpTreeWalker**: Decision tree traversal with "I don't know" fallback
- **ContextBuilder + KnowledgeRetriever**: Depth-aware knowledge injection

### Critical Pitfalls
1. **The Template Trap** — Move from slot-filling to intent-driven composition
2. **Dialogue Fatigue** — Hard 3-question limit before first draft
3. **Flat Keyword Knowledge** — Design ontology before writing content
4. **Keyword-Level Understanding** — Replace weighted scoring with rejection-based matching
5. **PyInstaller Packaging** — Use --onedir, gzip knowledge, lazy-load
6. **Industry Sprawl** — Hard limit of 5 industries, "deepen before widen"

## Implications for Roadmap

### Phase 1: Foundation — Schema + Test Industry Pack
Delivers: YAML schema, follow-up tree JSON schema, one complete test industry pack (互联网/IT).

### Phase 2: Knowledge Layer — Loader, Manager, Retriever
Delivers: KnowledgeLoader, KnowledgePack, KnowledgeManager, KnowledgeRetriever.

### Phase 3: Context Layer — State Management
Delivers: ConversationContext, ConversationTurn, SessionManager, ContextBuilder.

### Phase 4: Conversation Core — Engine + Classifier + Tree Walker
Delivers: ConversationEngine (9-state), IntentClassifier, FollowUpTreeWalker.

### Phase 5: Generation — Retriever + Generator V2
Delivers: KnowledgeRetriever, PromptGenerator v2 (intent-driven composition).

### Phase 6: UI — Conversational Interface
Delivers: AppController, ConversationalView, refinement panel.

### Phase 7: Scale — Remaining 4 Industry Packs
Delivers: Complete packs for 销售/零售, 教育, 金融, 制造业.

### Phase 8: Packaging — PyInstaller Build + Distribution
Delivers: --onedir build, compressed knowledge, Chinese Windows testing.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | YAML->JSON pipeline, JMESPath, dataclasses — well-established patterns |
| Features | MEDIUM | 8-dimension model reasoned, task frequencies need validation |
| Architecture | MEDIUM | State machine + decision tree is sound, depth limits need testing |
| Pitfalls | MEDIUM-HIGH | Concrete prevention strategies, some failure rates need validation |

## Sources
- v3.0 codebase analysis (knowledge.py, engine.py, generator.py, app.py)
- Python 3.12 stdlib, JMESPath spec, PyInstaller docs
- Published post-mortems of AIPRM, PromptBase, FlowGPT
- Conversational UI design literature
- Knowledge management ontology literature

---

*Research completed: 2026-06-03*
*Ready for roadmap: yes*
