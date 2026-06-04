---
phase: 06-ui
plan: 03
type: execute
subsystem: v4 UI
tags: [compliance, optimization-panel, knowledge-visibility, QA-03, UI-03, UI-04]
provides:
  - Optimization panel (collapse/expand, regenerate)
  - Compliance disclaimer (finance/manufacturing)
  - Knowledge pack visibility popup
  - Compliance banner UI in results
affects:
  - prompt_tool/app.py — v4 result page restructured (2-column grid)
  - prompt_tool/app_controller.py — refine_prompts added
  - prompt_tool/generator.py — COMPLIANCE_DISCLAIMERS + _compliance_disclaimer
  - tests/test_generator_v2.py — TestComplianceDisclaimer (4 tests)
tech-stack:
  added: []
  patterns:
    - Compliance: dual-layer (generator injects text + UI shows banner)
    - Panel toggle: grid_columnconfigure weight change + grid_remove
    - Modal: CTkToplevel + grab_set for knowledge pack popup
key-files:
  created: []
  modified:
    - prompt_tool/app.py: optimization panel, compliance banner, knowledge pack popup
    - prompt_tool/app_controller.py: refine_prompts method
    - prompt_tool/generator.py: COMPLIANCE_DISCLAIMERS, _compliance_disclaimer
    - tests/test_generator_v2.py: TestComplianceDisclaimer
decisions:
  - D-11: Right-side optimization panel with input/style/constraints/regenerate
  - D-12: Regenerate triggers full re-generation via PromptGeneratorV2
  - D-13: Panel default-expanded, collapse via toggle button in header
metrics:
  duration: "~15 min"
  completed_date: "2026-06-04"
---

# Phase 6 Plan 03: Optimization Panel + Knowledge Visibility + Compliance

**One-liner:** Complete v4 result page with collapse-optimization panel for refinement, compliance disclaimer SDK for finance/manufacturing prompts plus UI banner, and CTkToplevel knowledge pack overview modal.

## Summary

Plan 03 delivered the remaining v4 result page features:

1. **Compliance disclaimer (QA-03):** PromptGeneratorV2 injects a compliance disclaimer into all three prompt strategies for "finance" and "manufacturing" industries. The disclaimer includes industry-specific regulatory warnings (investment advice for finance, safety standards for manufacturing). Supports both English IDs (`finance`/`manufacturing`) and v3 Chinese keys (`金融`/`制造`).

2. **Optimization side panel (UI-03, D-11/12/13):** Right-side collapsible panel in the result page with a multi-line text input for additional requirements, a style dropdown (5 options: current/succinct/detailed/professional/accessible), three constraint checkboxes (word limit, include examples, plain text), and a regenerate button. Panel defaults to expanded; clicking the header toggle button collapses it, allowing the three strategy cards to fill the full width.

3. **Knowledge pack popup (UI-04):** CTkToplevel modal window triggered by "Knowledge Pack" button in both chat and result page headers. Shows all loaded industries with icon, name, statistical counts (terms, scenarios, trees, roles, workflows), description, and current-industry highlighting.

4. **Compliance banner UI (QA-03):** Yellow warning banner at the top of the result page for finance/manufacturing results, hidden for all other industries. Dynamic update on regenerate to reflect the new result's industry.

## Commits

| Hash | Type | Message |
|------|------|---------|
| 9d8925f | test | test(06-ui-03): add failing tests for compliance disclaimer in finance/manufacturing |
| 3a74910 | feat | feat(06-ui-03): implement compliance disclaimer for finance/manufacturing |
| 5a7fe18 | feat | feat(06-ui-03): implement optimization side panel and refine_prompts |
| 3ae1d59 | feat | feat(06-ui-03): implement knowledge pack popup and compliance banner UI |

## Changes by File

### prompt_tool/generator.py (+62/-1)
- Added `COMPLIANCE_DISCLAIMERS` class constant with finance and manufacturing disclaimer texts
- Added `_COMPLIANCE_KEY_MAP` for v3 Chinese key to v4 English ID mapping
- Added `_compliance_disclaimer()` method checking both `self.industry_id` and `self.r.get("industry_key")`
- Modified `generate_all()` to append disclaimer after anti-pattern filtering for sensitive industries

### prompt_tool/app_controller.py (+47/-0)
- Added `refine_prompts()` method: records to session, rebuilds context, re-invokes PromptGeneratorV2
- Added `session_manager` import

### prompt_tool/app.py (+434/-13)
- Restructured `_build_v4_result_page()` to 3-row 2-column grid layout (header, compliance banner, cards+panel)
- Added compliance banner frame with label in result page (hidden by default)
- Added `_build_optimization_panel()`: 280px-wide right panel with input box, style combo, constraint checkboxes, regenerate button
- Added `_toggle_optimization_panel()`: grid_remove/restore panel with column weight adjustment
- Added `_on_opt_regenerate()`: collects parameters, dispatches background thread for refine_prompts
- Added `_v4_on_refined()`: updates cards and compliance banner after refinement
- Added `_update_compliance_banner()`: shows/hides banner based on industry_id
- Added `_on_show_knowledge_pack_v4()`: CTkToplevel modal with industry cards, stats, current-highlight
- Enabled chat page Knowledge Pack button
- Added result page Knowledge Pack button

### tests/test_generator_v2.py (+82/-0)
- Added `TestComplianceDisclaimer` class with 4 tests:
  - `test_finance_prompts_contain_compliance`
  - `test_manufacturing_prompts_contain_compliance`
  - `test_non_sensitive_industry_no_crash`
  - `test_compliance_contains_disclaimer_phrases`

## Deviations from Plan

### Task ordering
The plan specified Task 1 as compliance (TDD), Task 2 as optimization panel (TDD), Task 3 as knowledge pack + compliance banner. During implementation, the result page grid restructuring (Task 2) logically required the compliance banner placeholder (Task 3 component) to be integrated in the same pass. The compliance banner structure was built during Task 2 to avoid reworking the grid layout twice. Task 3 then added the compliance banner logic and knowledge pack popup on top of the already-built frame.

No functional deviations from the plan specification.

## Verification

| Requirement | Status | Verification |
|-------------|--------|-------------|
| QA-03 compliance disclaimer (finance) | PASS | Generated prompts for "finance" contain "合规声明" or "不构成" in all 3 strategies |
| QA-03 compliance disclaimer (manufacturing) | PASS | Generated prompts for "manufacturing" contain "合规" or "安全规范" in all 3 strategies |
| QA-03 non-sensitive no crash | PASS | "internet_it" prompts generate without error and without forced compliance |
| UI-03 optimization panel | PASS | Panel builds, defaults expanded, toggle works, style combo has 5 options, regenerate button exists |
| UI-04 knowledge pack popup | PASS | `_on_show_knowledge_pack_v4` creates CTkToplevel, current industry highlighted, stats displayed |
| Full test suite | PASS | 124/124 tests pass |

## Self-Check: PASSED

All created files verified:
- [x] prompt_tool/generator.py — compliance disclaimer methods
- [x] prompt_tool/app_controller.py — refine_prompts
- [x] prompt_tool/app.py — optimization panel, compliance banner, knowledge pack popup
- [x] tests/test_generator_v2.py — TestComplianceDisclaimer (4 tests)
- [x] All 4 commits verified in git log
- [x] Full test suite green (124 passed)
- [x] End-to-end Python assertions pass
