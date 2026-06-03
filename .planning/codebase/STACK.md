# Technology Stack

**Analysis Date:** 2026-06-03

## Languages

**Primary:**
- Python 3.12+ (environment: 3.14.4) - All application code

**Secondary:**
- Not detected (pure Python project)

## Runtime

**Environment:**
- Python runtime, desktop application (tkinter-based GUI)

**Package Manager:**
- pip (via requirements.txt)
- Lockfile: Not present (no requirements-lock.txt or pip freeze output committed)
- Virtual environment: `.venv/` (created with `uv`/venv)

## Frameworks

**Core:**
- customtkinter 5.2.2 - Modern themed tkinter GUI framework for the desktop UI
- tkinter (stdlib) - Base GUI toolkit, used for messagebox, clipboard operations

**Testing:**
- Not detected (no test framework configured)

**Build/Dev:**
- PyInstaller - Bundles the application into a single Windows executable (`智能提示词工坊.exe`)

## Key Dependencies

**Critical:**
- `customtkinter>=5.2.2` - All UI components (buttons, text inputs, combo boxes, labels, frames)
- `pillow>=10.0.0` (Pillow 12.1.1 installed) - Image handling support (transitive dependency of customtkinter for theme assets/icons)

**Infrastructure:**
- None beyond the above. The application has zero network dependencies.

## Configuration

**Environment:**
- No `.env` file detected. No environment variables required.
- Application runs with zero configuration.

**Build:**
- `build.bat` - Windows batch script for PyInstaller packaging
- `run.py` - Entry point for PyInstaller `--onefile` packaging mode

## Platform Requirements

**Development:**
- Python 3.8+ (as noted in `build.bat`)
- Windows (target platform; PyInstaller builds Windows .exe)
- Packages: `customtkinter>=5.2.2`, `pillow>=10.0.0`

**Production:**
- Windows OS (the packaged .exe runs on Windows without Python)
- No internet connection required

---

*Stack analysis: 2026-06-03*
