# Domain Pitfalls: Offline Prompt Generation Tools & Industry Knowledge Systems

**Domain:** Offline prompt generation tool with embedded industry knowledge bases
**Researched:** 2026-06-03
**Confidence:** MEDIUM (substantial training knowledge, but unable to verify against current web sources — all findings should be validated during phase execution)

---

## Overview

This document catalogs the most common and costly mistakes made by similar projects. Each pitfall includes warning signs for early detection, specific prevention strategies, and which development phase should address it.

The project (v3.0) already demonstrates several of these pitfalls in its current codebase — the flat keyword dictionary, template-based generation, and source-level concerns. This document is designed to prevent those from recurring in v4.0 and to catch new pitfalls before they become embedded.

---

## CRITICAL PITFALLS

### Pitfall 1: The Template Trap — Generating Form Letters, Not Prompts

**What goes wrong:**
The tool generates prompts that read like Mad Libs fill-in-the-blank templates. Users get output that looks technically structured ("You are a [role]. Your task is [task]. Follow these steps: [steps].") but is generic, verbose, and ignores the specific context the user described. The prompt would work for almost any task, but works well for none.

**Why it happens (root cause):**
- The generation pipeline is structured as "template with slots" rather than "compose from primitives based on intent"
- The backend never truly understands the user's goal — it maps keywords to template IDs and fills blanks
- Templates are built for human readability, not for AI execution efficacy
- No distinction between prompt *structure* (which varies by task type) and prompt *content* (which varies by user context)
- v3.0 explicitly suffers from this: `generator.py` uses template filling with 3 strategies, each of which is a fixed structure

**Consequences:**
- Users try the tool once, get a generic result, and never return
- The tool's value proposition ("让AI真正干活的提示词") is actively undermined
- Users eventually discover that a simple direct instruction to ChatGPT works better than the "optimized" prompt
- Negative word-of-mouth: "it's just templates dressed up"

**Prevention strategy:**
- **Move from template slots to rule-based composition.** Define prompt components (persona, context, task, constraints, output format, examples) as composable building blocks. Each component is generated intelligently based on the analyzed intent, not pulled from a slot string.
- **Implement "prompt structure triage"**: Classify the user's task type (writing, analysis, brainstorming, translation, coding, planning, etc.) and select a prompt structure optimized for that task type, rather than applying a universal structure.
- **Add an "originality check"**: Before returning a generated prompt, compare it to known template outputs. If it's >70% similar to a template, regenerate with more variance.
- **Test against direct instruction**: For each generated prompt, have a test that answers: "Would the user be better off just typing their original request directly into ChatGPT?" If yes, the generation failed.

**Warning signs:**
- Generated prompts all have the same paragraph count and sentence structure regardless of the task
- You can replace `{行业}` and `{任务}` in the output without changing the rest of the text
- Users report "this looks like what I could have typed myself"
- The prompt reads more like a job description than a conversation starter
- Generated prompts use phrases like "请按照以下步骤" or "你的任务是" in every single output

**Phase to address:**
- **GEN-01** (Scenario-Aware Prompt Generator): This pitfall must be the primary design constraint for the generator architecture. Do not design GEN-01 as "fancy template system" — design it as "intent-driven composition engine."
- **QA-01** (Prompt Quality Evaluation): Build tests specifically for template detection. Flag any prompt that matches a template fingerprint above a threshold.

---

### Pitfall 2: Flat Keyword Knowledge That Looks Deep But Is Shallow

**What goes wrong:**
The knowledge base appears comprehensive (16 industries, 90+ task types) but all knowledge lives at a single level of detail: keyword = industry association. There is no hierarchy, no relationship structure, no workflow knowledge. The system "knows" that "KYC" belongs to finance, but doesn't know that KYC involves identity verification, risk assessment, ongoing monitoring, and regulatory reporting — each with different prompt needs.

**Why it happens (root cause):**
- Knowledge is collected by keyword scraping rather than domain analysis
- The team lacks domain experts for each industry and relies on their own intuition or shallow web research
- The flat-dict architecture (v3.0's `knowledge.py`) is easy to extend, so it keeps growing without structural improvement
- "More keywords = more knowledge" fallacy — quantity is mistaken for depth
- No knowledge ontology: terms, their relationships, their usage context, their priority

**Consequences:**
- The tool generates prompts that use industry jargon but in meaningless ways — "请按照金融行业合规要求进行分析" when the tool doesn't actually know what those requirements are
- Users with real industry expertise spot the shallowness immediately and lose trust
- The tool cannot handle compound requests ("帮我写一份Q2销售复盘报告，同时分析竞品动态") because the knowledge has no concept of task composition
- Knowledge conflicts: "数据" matched to 互联网_IT, 金融, 零售, and 教育 simultaneously, with no disambiguation

**Prevention strategy:**
- **Design a real knowledge ontology, not a tag list.** Each industry needs: entity terms (nouns), action terms (verbs), workflow sequences, quality criteria, common output formats, common misunderstandings.
- **Implement the "5 Whys" depth check**: For every term in the knowledge base, ask "Why is this term important for this industry?" 5 times. If you can't answer, the term is surface-level and should be flagged.
- **Build knowledge layers**: Layer 1 = keywords (current), Layer 2 = term relationships, Layer 3 = workflow context, Layer 4 = quality indicators. Generate prompts accessing all layers.
- **Use the knowledge graph approach** (KNOW-01): Store industry knowledge as a directed graph where terms connect to related terms, workflows, roles, and outputs. The prompt generator traverses the graph based on user intent, not keyword lookup.

**Warning signs:**
- Knowledge additions take < 30 minutes per industry (real depth takes days of analysis)
- Two "different" industries share >40% of the same keywords
- Knowledge file is a flat Python dict with no nested structure, no relationships
- A domain expert looks at the knowledge and says "this is technically correct but misses the point"
- Terms have no "weight" or "relevance score" — every keyword is equal

**Phase to address:**
- **KNOW-01** (Industry Expert Knowledge Package): This is the core design challenge. The knowledge ontology must be designed before any content is written.
- **KNOW-02** (Knowledge Package Auto-Build Pipeline): The pipeline must construct a graph, not a keyword list. Validate output against the "5 Whys" depth check.
- **KNOW-01 pilot phase**: Start with 1 industry (e.g., 互联网/IT where the team has most expertise), build the full ontology, validate it generates meaningfully better prompts. Then expand.

---

### Pitfall 3: Dialogue Fatigue — The Interrogation Trap

**What goes wrong:**
The conversational guidance system asks too many questions, asks the wrong questions, or asks them in a way that feels like an interrogation. Users abandon the tool mid-dialogue, or rush through answers providing low-quality input, resulting in prompts no better than if they'd just typed their original request.

**Why it happens (root cause):**
- Engineers design the dialogue tree from a "what does the system need to know?" perspective rather than "what can the user meaningfully answer?"
- Every new feature adds 2-3 more questions to the dialogue (scope creep)
- No consideration of cognitive load — each question forces the user to think and decide
- No progress indication — users don't know if they're on question 2 of 5 or question 2 of 20
- Questions are abstract ("What is your target audience?") rather than concrete ("Is this for your boss, your team, or external clients?")
- The v3.0 design was "input -> instant output" — changing to "input -> dialogue -> output" is a fundamental UX shift that risks breaking the simplicity the original tool was valued for

**Consequences:**
- High abandonment rate: >60% of users drop off after 3+ questions (industry average for conversational UIs)
- Answer quality degrades: users start giving one-word or random answers just to "get through it"
- Users who complete the dialogue feel exhausted, not empowered
- The tool's speed (2-second constraint) is wasted if the dialogue takes 2 minutes
- Users revert to typing their original simple request, bypassing the dialogue
- The dialogue becomes the bottleneck — the prompt generation itself is instant, but the "getting there" is painful

**Prevention strategy:**
- **3-question limit for cold start.** Maximum 3 questions before generating a first draft. Additional questions can appear as "optional refinements" after the user sees the first result.
- **Answer-first design.** Each question must pass this test: "Can a non-expert user answer this in <10 seconds?" If not, rephrase or eliminate. Replace "What industry framework does this need?" with "Is this for internal use or external/client-facing?"
- **Progressive disclosure pattern.** Show a progress bar and answer count. More importantly, let users see the draft prompt at any point — "Generate draft now" button always visible.
- **Delay deep questions.** Start broad (industry + task type), generate a rough draft immediately, then offer refinement questions as optional "tuning" on the side panel, not as a blocking dialogue.
- **Use defaults intelligently.** For every question, have a smart default based on what the system already knows. Don't ask if you can infer.
- **Implement the "one more thing" pattern.** After the main dialogue, offer exactly one refinement: "Want me to adjust the tone, add constraints, or add examples?" — user picks one, gets one follow-up question. That's it.

**Warning signs:**
- Dialogue tree has more than 5 top-level questions
- Questions take >15 seconds to read and understand
- There's no "skip" or "I don't know" option for any question
- Users report the tool as "needy" or "too demanding"
- Dialogue completion rate is below 50%
- The dialogue cannot be completed in under 60 seconds by a decisive user

**Phase to address:**
- **CONV-01** (Conversational Requirement Mining Engine): Design the dialogue tree with the 3-question limit as a hard constraint. Build the "generate draft at any point" escape hatch first, then add the dialogue flow.
- **CONV-02** (Deep Questioning Logic Tree): The "depth" should apply to the *refinement* phase, not the initial dialogue. The logic tree is for optional follow-ups, not the mandatory path.
- **UI-01** (Conversational Interface): Implement the progress bar and "Generate Draft Now" button in the first UI prototype. Test with real users before adding more dialogue features.

---

### Pitfall 4: Keyword-Level Understanding When Intent-Level Is Needed

**What goes wrong:**
The system interprets user input by matching keywords (v3.0's `engine.py` approach: keyword overlap scoring), which leads to systematic misunderstandings. The same word means different things in different contexts ("分析" in sales vs. data science vs. medical). The system doesn't understand *why* the user is asking, only what words they used.

**Why it happens (root cause):**
- Keyword matching is fast, simple, and works for obvious cases (80% accuracy), creating a false sense of competence
- The v3.0 scoring algorithm is legacy code that "works enough" — the team is reluctant to replace something functional
- True intent understanding requires either NLP models (violates offline constraint), verbose lookup tables (maintenance burden), or highly structured knowledge graphs (not yet built)
- No negative scoring: "数据" matching 金融 gets positive weight even when the user's context is clearly education

**Consequences:**
- **Category error cascade**: If industry detection is wrong, everything downstream is wrong. The user selects the correct industry manually, but this is friction that undermines the "auto" value prop.
- **Silent failure**: The system doesn't know it's wrong. It confidently generates an output for the wrong industry, and the user sees a prompt filled with irrelevant terminology.
- **Ambiguity in Chinese**: Chinese has less delimiter between words (no spaces), making keyword extraction inherently harder. "数据分析师" could match "数据"→互联网/IT, "分析"→金融, "分析师"→金融.
- **Scaling collapse**: As more industries are added, cross-industry keyword overlap increases non-linearly. The scoring algorithm's error rate grows with every new industry.
- The CONCERNS.md already identifies this: scoring weights are arbitrary, never tuned against a test dataset.

**Prevention strategy:**
- **Replace weighted keyword scoring with rejection-based classification.** Instead of "which industry scores highest?", use "which industries are clearly not a match?" and only have the dialogue clarify the remainder. This is more robust with fewer false positives.
- **Implement "confidence threshold + fallback".** When the top industry match is below a confidence threshold, don't guess — instead, say "I'm not sure about the industry. Are you in [候选项A], [候选项B], or something else?" The CONCERNS.md suggests this already.
- **Build industry disambiguation pairs.** For each high-conflict keyword (appears in N industries), define the distinguishing context for each industry. E.g., "数据 + 增长率 = 零售电商, 数据 + 算法 = 互联网/IT".
- **Use multi-pass analysis.** Pass 1: broad keyword matching (current approach). Pass 2: context verification using the dialogue responses. Pass 3: intent refinement using the first generated draft as a "probe" that the user can correct.
- **Let the user correct early.** Show the detected industry and task in the UI *before* generating. If wrong, user picks the right one. This is a one-click correction vs. regenerating fully.

**Warning signs:**
- Industry auto-detection accuracy <90% on known test inputs
- Users regularly override the industry dropdown
- A single word change in input completely changes industry detection
- "数据" matches 3+ industries with similar scores
- Adding a new industry causes existing detection accuracy to drop

**Phase to address:**
- **ENGINE-REFACTOR** (phase this as the first technical task after planning): Before building new knowledge, fix the classification engine. Add confidence thresholds, disambiguation pairs, and rejection-based matching.
- **CONV-01** (Dialogue): Use the dialogue not just to gather information, but to verify and correct the classification engine's output.
- **UI-01**: Show detected industry/task prominently and allow one-click correction.

---

### Pitfall 5: The Cold Start Trap — Expecting Users to Know What They Want

**What goes wrong:**
The tool assumes the user arrives with a clear, well-formed request. It provides a single input box ("请输入你的需求描述"). Users who know exactly what they want can use this fine — but the target audience ("不懂写提示词的普通人") often has only a vague idea. They type something incomplete, get a mediocre result, and the tool never helps them discover what they *actually* need.

**Why it happens (root cause):**
- The single-input-box pattern is inherited from chatbot UIs and search bars — it's what users expect, but it's wrong for guided generation
- The v3.0 codebase has a single text input as the primary interaction point
- Team assumes "user types -> AI generates" is the natural flow
- No scaffolding: the tool offers no help for users who don't know what to write
- The "blank page problem" is well-studied in creativity tools but rarely addressed in prompt generators

**Consequences:**
- Users type "帮我写个方案" — too vague. Tool generates a generic template. User concludes the tool is useless.
- Users type "我要写一封邮件给客户" — somewhat better, but still missing context (what kind of client? about what? what outcome?). Tool can't generate a great prompt from this.
- The tool's best feature (deep industry knowledge) is never triggered because the user never typed specific enough keywords
- Power users learn to type detailed inputs and get good results, but casual users never reach this point
- The tool ends up serving only the "already know what they want" demographic — the exact opposite of the intended audience

**Prevention strategy:**
- **Replace the blank input with structured cold-start options.** "What do you need?" presented as categorized templates: writing, analysis, planning, learning, translation, creative. Each choice leads to a more specific sub-choice. This is a 2-click cold start path for confused users.
- **Implement "progressive elaboration".** Start with the user's raw input (even if it's 3 words). Generate a draft. Show the draft alongside a "refinement panel" where the user can add specifics (industry, tone, format, constraints). The conversation starts *after* the first draft, not before.
- **Use the "example prompt" pattern.** Show 2-3 examples of good inputs for the detected industry: "来看看别人在 [行业] 是怎么写的？" Clicking an example fills the input and demonstrates the expected depth.
- **Implement an "unknown start" flow.** If the system detects low confidence in industry/task classification, enter a guided discovery mode: "让我帮你定位需求。这是为了工作还是个人用途？→ 是什么类型的工作？→ ..." This should be a distinct path from the "I know what I want" path.
- **Add a "deepen request" suggestion.** After user types something short, automatically suggest expansions: "你的需求可以更具体——比如目标读者是谁？希望达到什么效果？" This teaches users to write better inputs over time.

**Warning signs:**
- >30% of user inputs are under 10 Chinese characters
- Users generate multiple times without changing input (hoping for different results)
- Industry auto-detection fails frequently on first-time user inputs
- Users ask "这工具能做什么？" — meaning the tool's purpose isn't self-evident
- The input box is empty when the tool launches (it should show guidance text or examples)

**Phase to address:**
- **UI-01** (Conversational Interface): The cold start experience is the first thing users see. Design it in the first UI prototype. The "input box" from v3.0 must be replaced with a choice-driven start.
- **CONV-01**: The dialogue engine must have a "low confidence" branch that does discovery before requirement gathering.
- **GEN-01**: The generator must be able to work with partial information and improve as more context is added (incremental refinement, not regenerate-from-scratch).
- **CONTENT-01** (not yet in requirements — add it): Create example inputs and cold-start guides for each of the 5 target industries.

---

### Pitfall 6: Security/Ethical Blind Spots in Sensitive Industries

**What goes wrong:**
The tool generates prompts for 金融, 医疗, 法律 without safeguards. A doctor uses the tool to generate a "diagnostic protocol prompt" for an AI. A financial advisor uses it to generate a "compliance analysis prompt." The AI then produces output that looks authoritative but is wrong, and because the tool was "expert-level," the user trusts the AI output more than they should.

**Why it happens (root cause):**
- "It's just a prompt generator" attitude — team assumes no responsibility for how prompts are used
- The offline nature creates false security ("we're not processing any data, just generating text")
- Industry knowledge in the tool makes it *appear* authoritative, even when the team explicitly disclaims it
- No differentiation between "this industry's common terminology" and "this industry's regulated practices"
- Legal liability is unclear and hard to assess, so the team doesn't assess it at all
- Chinese regulations (生成式人工智能管理办法, 2023) require providers of generative AI tools to ensure content is lawful. While the tool generates prompts (not AI content), the boundary is legally gray.

**Consequences:**
- **Liability exposure**: If a generated prompt leads a 法律 professional to use AI for "case analysis" and the AI hallucinates a precedent, who is responsible?
- **Reputation damage**: A single news story ("提示词工具生成错误医疗建议") could end the project
- **Regulatory risk**: China's AI regulations are tightening. A tool that generates prompts for regulated industries could fall under supervision
- **Unintentional harm**: A generated prompt in 金融 might instruct the AI to "analyze this investment risk" — the AI might make a flawed analysis that a non-expert user acts on
- **User data risk**: Even offline, users may type sensitive information (patient data, trade secrets, legal case details) into the tool. The prompt output (copied to clipboard, pasted into web AI) then exposes this data

**Prevention strategy:**
- **Industry-specific content warnings.** For 金融, 医疗, 法律, show a clear disclaimer before and after generation: "本工具生成的提示词仅供参考。专业判断请咨询持牌人士。AI输出不应替代专业意见。"
- **Refuse to generate for regulated tasks.** Certain task types (diagnosis, legal judgment, compliance certification) should trigger a warning and an explicit user confirmation: "我理解AI的输出不是专业建议" checkbox.
- **Implement output content filtering.** Before returning a generated prompt, scan for patterns that suggest regulated advice (prescription, diagnosis, legal ruling, investment advice). Flag or block these.
- **Do not include "expert authority" framing in prompts.** Generated prompts should never start with "作为资深金融专家" — this misleads the AI's output authority. Use role descriptions that clarify limitations: "你是一个分析助手，仅提供参考信息。"
- **Add a "critical use" checklist.** Before first use in a sensitive industry, show a one-time notice: understand AI limitations, don't input personal data, don't rely solely on AI output.
- **Clipboard warnings for sensitive content.** If the generated prompt contains financial/medical/legal terminology, add a one-line warning when user copies: "该提示词涉及专业领域，请审慎使用。"
- **Consult Chinese legal counsel** about whether prompt generation for regulated industries requires content moderation mechanisms under the 生成式人工智能服务管理暂行办法.

**Warning signs:**
- The team has not discussed legal liability for any generated prompt
- No disclaimers exist anywhere in the UI
- The tool doesn't distinguish between "this industry's terminology" and "this industry's regulated practices"
- Users could generate a prompt for "诊断该患者的症状并推荐治疗方案" without any warning
- The tool uses phrases like "作为权威[行业]专家" in generated prompts
- There is no record of what content was generated (for legal defense in case of dispute)

**Phase to address:**
- **GEN-01**: Design prompt generation to avoid fake authority framing. Role descriptions should be honest about AI limitations.
- **UI-01**: Add industry-specific disclaimers and warning banners. Design the consent flow for regulated industries.
- **PKG-01**: Ensure the exe includes all disclaimer text and cannot be bypassed.
- **GA-01** (Governance — new suggested phase): Before the first public release of v4.0, conduct a legal review of the generated content risk. Create a safety checklist for each regulated industry.
- **SEC-01** (Security — new suggested phase): Add input scanning for PII/PHI warnings and clipboard safety notices.

---

### Pitfall 7: PyInstaller Packaging Catastrophes for Knowledge-Heavy Apps

**What goes wrong:**
As the knowledge base grows (deep industry packages, dialogue trees, generation rules), the PyInstaller exe becomes bloated, slow to start, and prone to crashes. The "single file <50MB" constraint becomes impossible to maintain. Users on older Windows machines experience 30+ second startup times, false antivirus positives, and mysterious crashes with Chinese file paths.

**Why it happens (root cause):**
- `--onefile` mode extracts all contents to a temp directory on every launch — a 50MB archive takes 5-30 seconds to extract on mechanical drives
- Knowledge data is stored as Python modules (.py files), which PyInstaller bundles but cannot compress efficiently
- Chinese filename support in PyInstaller is notoriously fragile — temp directories with Chinese characters (用户目录/AppData/Local/Temp/...) cause extraction failures
- Antivirus software (especially on Chinese Windows: 360, Tencent) aggressively quarantines single-file exes with embedded data payloads
- Knowledge updates require a full exe rebuild and redistribution — there's no delta update mechanism

**Consequences:**
- **50MB exe becomes 150MB+** as knowledge depth increases: 16 industries x 5 knowledge layers x rules x templates = serious bloat
- **Startup time degrades** from "instant" to "go make coffee" — violating the "双击即用" value prop
- **Antivirus false positives** increase with exe size and embedded data — users download once, AV deletes it, user never tries again
- **Chinese path crashes**: User on Chinese Windows with Chinese username gets an extraction error because the temp path has Chinese characters the embedded data can't handle
- **No incremental updates**: Every knowledge fix (e.g., "金融_P2P规则已过时") requires shipping a new 50MB+ exe
- **No user notification**: The exe silently fails to extract on some machines, and there's no diagnostic output

**Prevention strategy:**
- **Use `--onedir` instead of `--onefile`.** This extracts the directory once and reuses it. Startups are instant after first launch. The user gets a folder with the exe inside — still "双击即用" if we provide a shortcut.
- **Split knowledge from code.** Keep knowledge data in compressed JSON/YAML files within the PyInstaller bundle, not in Python modules. Compress knowledge files (gzip) inside the exe and lazy-decompress on first use per industry.
- **Implement lazy loading of knowledge packages.** Do not load all 5 target industries' knowledge at startup. Load only the detected industry's package. Keep others compressed. This dramatically reduces memory and startup time.
- **Test on Chinese Windows specifically.** Set up a test VM with Chinese Windows 10/11, Chinese username, Chinese file paths. Run the PyInstaller build and confirm extraction and launch work.
- **Add a startup self-test.** On first launch, verify that all knowledge packages can be extracted and loaded. If not, show a diagnostic message (in Chinese) with next steps.
- **Use 7zip/UPX compression.** PyInstaller supports UPX compression for binaries. For knowledge data, use gzip or brotli compression to reduce size at the cost of decompression time at first use.
- **Consider NSIS installer as alternative.** An installer (instead of single-file exe) can extract to Program Files, handle Chinese paths correctly, and provide a Start Menu shortcut. This is more resilient than --onefile.

**Warning signs:**
- The `--onefile` exe takes >10 seconds to start on a modern SSD
- Any build produces an exe >80MB
- Knowledge files are plain Python modules (.py) with no compression
- No one has tested the build on an actual Chinese Windows machine with a non-ASCII username
- The PyInstaller build has not been tested with the knowledge package format (will be, since KNOW-01 is new)
- Updates to one industry's knowledge requires rebuilding and shipping the entire exe

**Phase to address:**
- **PKG-01** (Offline Exe Packaging): This phase must be planned as a significant engineering effort, not a 1-day task. Factors:
  - Knowledge package format (compressed JSON or SQLite)
  - Lazy loading infrastructure
  - `--onedir` migration
  - Chinese path testing
  - UPX/brotli compression
  - Antivirus whitelisting strategy
- **KNOW-01**: Must design the knowledge package format in parallel with PKG-01. The format choice (JSON vs YAML vs SQLite vs Python dict) directly impacts packaging strategy.
- **INFRA-01** (new suggested phase): Create a build pipeline with automated testing on Chinese Windows VM before any release.

---

### Pitfall 8: Industry Sprawl — Trying to Cover Everything, Mastering Nothing

**What goes wrong:**
The tool tries to support too many industries (currently 16, planned to expand). Each new industry gets a fraction of the team's attention. The knowledge for each is shallow, the dialogue trees are generic, and the prompts are template-level. No single industry gets "expert-depth" treatment. The tool is a mile wide and an inch deep — and users from every industry can tell.

**Why it happens (root cause):**
- "More industries = more users = more value" fallacy — the team confuses breadth with value
- Sales/marketing pressure: "We need to show coverage for [hot industry]"
- Fear of exclusion: "If we don't support [industry], users from that industry won't use the tool"
- The codebase makes adding a new industry easy (add keywords to a dict), creating a low-cost illusion
- No industry-specific quality bar — every industry passes the same minimal validation
- No user feedback mechanism per industry — the team doesn't know which industries actually have users

**Consequences:**
- **Quality floor drops**: The average quality across all industries is mediocre, so no industry advocates for the tool
- **Maintenance burden grows**: Each new industry adds knowledge maintenance, testing matrix multiplication, and dialogue tree complexity
- **Detection ambiguity increases**: As noted in Pitfall 4, more industries = more cross-industry conflicts = more wrong auto-detection
- **Team focus is diluted**: Instead of making 3 industries excellent, the team makes 16 industries "okay"
- **The "why not ask ChatGPT directly?" question intensifies**: If the tool adds no real depth, users ask "why not just ask ChatGPT? It already knows about all industries"
- **Resource starvation**: The 5 core industries (互联网/IT, 销售/零售, 教育, 金融, 制造业) don't get enough attention because team is maintaining the other 11

**Prevention strategy:**
- **Hard limit: maximum 5 industries for v4.0.** Enforce this in the requirement spec. The project already has this intention (GEN-02), but it must be enforced against scope creep.
- **Define "industry depth completion criteria"** before expanding. Each core industry must pass:
  - 50+ structured knowledge terms with relationships defined
  - 10+ distinct task types with differentiated prompt structures
  - Dialogue tree with 3+ industry-specific questioning paths
  - Test suite with 20+ test inputs that produce differentiated outputs
  - Reviewed by someone with industry experience (or based on vetted research)
  - Quality score >= 4/5 on an internal evaluation rubric
- **Kill industries with no usage.** After launch, track which industries are actually used. If an industry has <5% of users after 3 months, drop it from active maintenance. Move to "community-supported" tier.
- **"Deepen before widen" rule.** For every planned new industry, first add one more depth layer to an existing core industry. Only after deepening can widening be considered.
- **Industry knowledge ROI analysis.** Before adding an industry, estimate: how many users will this attract? How many knowledge terms needed? How many dialogue paths? What's the maintenance cost/year? If 1 core industry serves 20% of users and 1 new industry serves 2%, the math is clear.

**Warning signs:**
- TODO list has "[行业] 基础知识包" items but no "[行业] 深度验证" items
- Knowledge files for different industries are all roughly the same size (indicating template-level, not depth-level)
- Team members disagree on which industries are "core"
- "Just add a few keywords for [new industry]" requests come weekly
- No one on the team has actually worked in the target industries
- User feedback mentions "it works but [industry] parts are shallow"
- The codebase still has the 16-industry flat structure from v3.0

**Phase to address:**
- **Planning/Kickoff**: Set the 5-industry limit as a non-negotiable project constraint. Document the criteria for "depth completion."
- **GEN-02**: This requirement explicitly says "3-5 industries at extreme depth." The limit must be enforced even if stakeholders push for more.
- **KNOW-01**: Build knowledge depth frameworks (graph/ontology) that make it obvious when depth is incomplete. If a knowledge package doesn't have all layers, it's visibly unfinished.
- **QA-01**: Create industry-specific quality rubrics that must be passed before an industry is considered "releasable."
- **GOV-01** (governance — new suggestion): Create a decision framework for industry expansion. "New industry X requires: team member or advisor with X experience, 40 hours of knowledge work, positive quality score on 20 test cases."

---

## MODERATE PITFALLS

### Pitfall 9: The "More Rules = Better" Trap in Prompt Generation Logic

**What goes wrong:**
The generator accumulates hundreds of "special case" rules and conditionals ("if industry is 金融 and task is 分析 and user mentions 合规, add compliance paragraph"). The generation logic becomes a tangled mess of if-else chains that no one fully understands. Adding new industries or tasks breaks old rules. The code becomes unmaintainable.

**Prevention strategy:**
- Use a rule engine or decision table, not nested if-else. Rules should be data, not code.
- Limit to 3 levels of conditional nesting maximum. If a rule needs 4+ conditions, it should be a separate component.
- Implement a "rule impact test" — each new rule must be tested against all 50+ existing test inputs to ensure no regression.

**Phase: GEN-01** — the generator architecture must support rules as data from day 1.

---

### Pitfall 10: Optimizing for AI Executors Instead of Human Readers

**What goes wrong:**
The generated prompt is optimized to produce good results from Claude/GPT, but is unreadable or overwhelming to the human who needs to review and paste it. Prompts that are 2000+ words with complex XML formatting intimidate casual users. They don't trust what they can't understand.

**Prevention strategy:**
- Always generate a "human summary" alongside the prompt: "我将给AI发送以下指令：[3句话摘要]。完整的提示词如下：[详细版]"
- Use progressive disclosure: show a brief prompt first, with an "expand to detailed version" option
- Test prompts with non-technical users in user testing — can they understand what the prompt does?
- Follow the "one screen" rule: the generated prompt should fit on one screen without scrolling, if possible

**Phase: GEN-01, UI-01**

---

### Pitfall 11: Ignoring the Continuation Problem — Users Iterate

**What goes wrong:**
The tool treats each generation as a one-shot operation. But real prompt engineering is iterative: the user tries the prompt, gets results, and wants to tweak. If every tweak requires going through the full generation pipeline again (re-typing input, re-answering dialogue questions), users give up.

**Prevention strategy:**
- Implement "edit and regenerate" — the generated prompt should be editable in the UI, with a "regenerate based on edits" button that considers both the original input and the user's edits
- Save the full generation context (input, dialogue answers, industry, task) so the user can return and tweak
- Implement version history: "previously generated prompts" dropdown so users can compare versions

**Phase: UI-01, CONV-01 post-MVP**

---

### Pitfall 12: Knowledge Package Silos — No Cross-Industry Pattern Reuse

**What goes wrong:**
Each industry team (or each knowledge package) builds its own ontology, dialogue tree, and generation rules from scratch. Common patterns across industries (all industries need "write a report" prompts, all industries have "analyze this data" tasks) are duplicated. 5 industries x 5 dialogue paths = 25 unique implementations that could be 5 base paths + 5 overrides.

**Prevention strategy:**
- Design a "cross-industry core" knowledge layer first: task types, persona templates, output formats, constraint types that are universal
- Each industry package only defines what differs from the core: specific terminology, industry workflows, relevant regulations
- Implement "inheritance" in knowledge packages: 金融.prompt_base inherits from core.prompt_base and overrides terminology, adding compliance constraints

**Phase: KNOW-01 design phase**

---

### Pitfall 13: Chinese NLP Assumptions That Don't Hold in Practice

**What goes wrong:**
The engine uses simple word-boundary heuristics (character n-grams, space splitting) that fail for Chinese text. Chinese has no word delimiters. "上海市市长" contains "上海", "上海市", "市长", "海市" — most are meaningless as keywords. The v3.0 bigram/trigram approach generates noise.

**Prevention strategy:**
- Use jieba (or a similar Chinese tokenizer) for word segmentation instead of n-grams. It's offline-capable and handles Chinese significantly better.
- Build a domain-specific lexicon of known terms per industry for the tokenizer to prefer
- Test with real Chinese user inputs from each industry, not idealized examples

**Phase: ENGINE-REFACTOR** — this is a foundational fix needed before KNOW-01 is built on top.

---

## MINOR PITFALLS

### Pitfall 14: Thread Safety Ignored in Worker Thread

Already documented in CONCERNS.md — mutable instance attributes written from background thread without locks. This will get worse as the knowledge system and dialogue engine add more shared state.

**Prevention:** Implement a proper state machine for the generation pipeline with explicit state transitions and thread-safe state reads. Or use a message-passing pattern (queue-based) instead of shared state.

**Phase: ENGINE-REFACTOR, UI-01**

---

### Pitfall 15: No User Feedback Loop — Flying Blind on Quality

**What goes wrong:**
The team builds knowledge and generation rules based on internal assumptions, with no mechanism to learn from actual user experience. Bad prompts get generated indefinitely because no one knows they're bad.

**Prevention:**
- In v4.0 (which is offline), implement an optional anonymous telemetry that records: input length, detected industry, generated prompt length, whether user copied/exported. No personal data, just usage patterns.
- Add a simple "thumbs up/thumbs down" on generated prompts. Store feedback locally. Export for team analysis when user opts in.
- Build a test harness with 50+ user-simulated inputs per industry, and run quality scoring on every knowledge update.

**Phase: QA-01, INFRA-01**

---

### Pitfall 16: Culture-Specific Prompt Patterns Applied Universally

**What goes wrong:**
Prompt patterns that work well for English (chain-of-thought, role-playing, negative constraints) are applied mechanically to Chinese prompts without adaptation. CoT prompts that are effective in English become verbose in Chinese. "请一步一步思考" works differently than "Let's think step by step" because Chinese LLMs are trained on different data distributions.

**Prevention:**
- Test generated Chinese prompts against Chinese LLMs (文心一言, 通义千问) and also against ChatGPT/Claude in Chinese. The optimal pattern may differ.
- Research Chinese-specific prompt engineering patterns (角色前置, 分步拆解, 具象化示例)
- Prefer concrete examples over abstract instructions — Chinese prompt engineering community consistently values few-shot examples more than English community

**Phase: GEN-01, QA-01**

---

## Phase-Specific Warning Map

| Development Phase | Likeliest Pitfall | Mitigation Approach |
|---|---|---|
| **KNOW-01** (Knowledge Packages) | Pitfall 2 (shallow knowledge), Pitfall 8 (industry sprawl), Pitfall 12 (no cross-industry reuse) | Design ontology first, enforce 5-industry hard cap, build core layer before industry-specific |
| **KNOW-02** (Auto-Build Pipeline) | Pitfall 2 (auto-built knowledge is shallow if not validated), Pitfall 9 (build rules that don't transfer) | Require human validation of auto-built knowledge. Use auto-build as draft, not final. |
| **CONV-01** (Dialogue Engine) | Pitfall 3 (dialogue fatigue), Pitfall 5 (cold start), Pitfall 11 (no continuation) | 3-question hard limit, "generate draft now" escape hatch, answer-first design |
| **CONV-02** (Deep Questioning Logic) | Pitfall 3 (depth becomes interrogation), Pitfall 9 (too many special-case paths) | Apply depth in refinement phase only, not mandatory path. Rules as data, not if-else. |
| **GEN-01** (Prompt Generator) | Pitfall 1 (template trap), Pitfall 6 (ethical failures), Pitfall 10 (unreadable prompts) | Intent-driven composition, authority-framing filter, human summary generation |
| **GEN-02** (5-Industry Depth) | Pitfall 8 (scope creep beyond 5), Pitfall 2 (depth measured by lines, not structure) | Hard industry limit, depth completion criteria, kill underperforming industries |
| **UI-01** (Conversational UI) | Pitfall 3 (fatigue), Pitfall 5 (cold start), Pitfall 10 (overwhelming output display) | Progress bar, cold-start choices vs. blank input, progressive disclosure |
| **PKG-01** (Offline Exe) | Pitfall 7 (PyInstaller catastrophe), Pitfall 2 (knowledge format incompatible with packaging) | --onedir, compressed knowledge format, lazy loading, Chinese path testing |
| **QA-01** (Quality Evaluation) | Pitfall 1 (no template detection), Pitfall 6 (no safety checks), Pitfall 15 (no user feedback) | Template fingerprinting, safety content scanning, industry-specific rubrics |

---

## Critical Questions Open for Phase-Level Research

These areas need deeper investigation before or during the relevant phase:

1. **Chinese tokenizer selection**: jieba vs. pkuseg vs. HanLP vs. lightweight alternatives. Testing needed for speed (2s constraint) and accuracy on domain-specific text (金融/医疗 terminology).

2. **Knowledge graph library for Python**: Options include NetworkX (pure Python, 0-dep), RDFLib (standard ontology support), or custom dict-of-dict. Test for performance with ~5000 nodes.

3. **Chinese-specific prompt effectiveness research**: What prompt patterns consistently work better for Chinese LLMs? This affects GEN-01 structure decisions.

4. **Legal review scope**: Which regulated industries (金融, 医疗, 法律) require what level of disclaimer? Engage Chinese legal counsel during QA-01 or earlier.

5. **PyInstaller knowledge format benchmark**: Test compressed JSON vs. SQLite vs. msgpack for embedded knowledge. Measure: file size, load time for single industry, load time for all industries. This affects both KNOW-01 and PKG-01.

6. **Dialogue tree effectiveness testing**: Before building the full CONV-02 logic tree, test a paper prototype with 5 users per target industry. Measure: completion rate, time to complete, user satisfaction. The specific questions matter more than the tree structure.

---

## Sources

This document is based on:
- Analysis of the v3.0 codebase (knowledge.py, engine.py, generator.py, app.py) and the documented concerns in CONCERNS.md
- Published post-mortems of prompt engineering tools (AIPRM, PromptBase, FlowGPT failure analyses known from training data)
- Industry knowledge management literature (ontology design, knowledge graph anti-patterns)
- PyInstaller community documentation on common failure modes for single-file distribution
- Chinese AI regulation (生成式人工智能服务管理暂行办法, 2023)
- Training data covering conversational UI design patterns and failure modes

**Confidence note:** All findings are derived from training knowledge and codebase analysis. They should be validated against current sources (web research, user testing, legal consultation) during the corresponding development phases. Specific claims about industry failure rates (e.g., ">60% abandonment after 3 questions") are from training data and may need fresh validation.
