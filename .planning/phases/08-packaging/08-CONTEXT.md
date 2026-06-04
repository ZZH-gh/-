# Phase 8: Packaging - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>
## Phase Boundary

将 v4.0 应用从 PyInstaller --onefile 迁移到 --onedir 模式，添加知识包 gzip 压缩，确保中文 Windows 兼容性。最终产物为 <50MB 的目录 exe，双击即用。

**本阶段交付：** 更新 build.bat、KnowledgeManager gzip 解压支持、run.py 中文兼容处理。
**本阶段不包含：** 功能代码改动、UI 改动、知识包内容改动。

</domain>

<decisions>
## Implementation Decisions

- **D-01:** build.bat 从 --onefile 改为 --onedir（已有代码，确认生效）。
- **D-02:** 知识包编译后 gzip 压缩存储，KnowledgeManager 按需解压加载（已有代码，需集成到加载路径）。
- **D-03:** run.py 添加中文路径兼容（sys.stdout.encoding、sys.setdefaultencoding 等）。
- **D-04:** build.bat 中保留 chcp 65001 确保中文编码正确。
- **D-05:** --onedir 模式下 --add-data 路径保留，确保 prompt_tool 包完整内置。

### Claude's Discretion
- KnowledgeManager 中 gzip 解压的具体实现细节
- 中文兼容测试的具体用例

</decisions>

<canonical_refs>
## Canonical References

- `.planning/ROADMAP.md` § Phase 8 — 阶段目标与成功标准
- `.planning/REQUIREMENTS.md` § PKG-01, PKG-02, PKG-03
- `build.bat` — 现有打包脚本，需更新
- `run.py` — 入口点，需添加中文兼容
- `prompt_tool/knowledge_manager.py` — 需添加 gzip 加载支持
- `prompt_tool/knowledge_packs_compiled/` — 编译产物目录

</canonical_refs>

<code_context>
### Reusable Assets
- `build.bat` — 已有完整的打包脚本框架，含 --onedir、gzip、chcp 65001

### Integration Points
- `build.bat` — 打包管线入口
- `prompt_tool/knowledge_manager.py` — load_pack() 中增加 .json.gz 解压路径
- `run.py` — 添加中文路径兼容初始化

</code_context>

<deferred>
## Deferred Ideas
- **NSIS 安装包**（PKG-04, v2 功能）
- **在线知识包更新**（PKG-05, v2 功能）

</deferred>

---

*Phase: 8-Packaging*
*Context gathered: 2026-06-04*
