# External Integrations

**Analysis Date:** 2026-06-03

## APIs & External Services

**None detected.**

This application is fully offline. It does not call any external HTTP APIs, REST services, or third-party SDKs. All functionality (keyword matching, prompt generation) runs locally.

- No OpenAI / LLM provider API calls
- No cloud service SDKs
- No weather, stock, or data fetching services

## Data Storage

**Databases:**
- None. No database system is used. All data is stored in-memory during runtime.

**File Storage:**
- Local filesystem only. The export feature writes text files to the user's Desktop directory (`%USERPROFILE%\Desktop\`).

**Caching:**
- None. No caching layer. All computation is performed on-demand.

## Authentication & Identity

**Auth Provider:**
- None. No user authentication, login, or identity management.

## Monitoring & Observability

**Error Tracking:**
- None. Errors are surfaced to the user via tkinter messagebox dialogs in the GUI.

**Logs:**
- No logging framework. Status messages are displayed in the UI status bar (`set_status()`). No persistent log files are written.

## CI/CD & Deployment

**Hosting:**
- Not applicable. This is a standalone desktop application.

**CI Pipeline:**
- None. No CI configuration files found (no `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.).

## Environment Configuration

**Required env vars:**
- None. The application requires no environment variables.

**Secrets location:**
- Not applicable. No secrets, API keys, or tokens are used anywhere in the codebase.

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None.

## Key Design Decision

The application is intentionally designed to be **fully offline and self-contained** (as stated in the module docstrings: "完全离线运行，不依赖任何外部API" / "fully offline, does not depend on any external API"). All 15 industry knowledge bases, keyword matching, task recognition, and prompt generation logic are embedded directly in the source code (`prompt_tool/knowledge.py`).

---

*Integration audit: 2026-06-03*
