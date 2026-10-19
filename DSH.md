# DSH.md · DeepSeek Harness 接手与运行条件

本文件只写平台相关的事；业务规则、方法、记忆以 `AGENTS.md` 和 `memory/` 为准。

## 当前执行方

- 2026-10-19 起，研究助理的对话端由 DSH（DeepSeek Harness）承接；入口在工作区 `research/`。
- 本 repo（`SHAWEINEIX/ResearchAssociate`）是规则、记忆、课题和脚本的唯一来源；工作区入口不另存一套。
- 平台变化时，先按 `AGENTS.md` 接手，再按本文档核对运行条件；不把旧平台记录当当前能力。

## 运行条件（2026-10-19 实测）

- **仓库**：`D:\deepseekharness-workspace\research\repo`，工作区内，`workspace-write` 即可读写和提交。
- **Python**：`D:\软件\Python\python.exe`（3.13，`Asia/Shanghai` 的 zoneinfo 可用）。脚本只用标准库；跑之前设 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`，否则 Windows 控制台会在中文与符号上报 `UnicodeEncodeError`。
- **Git 联网**：先点源 `. .\research\git-env.ps1`，再在同一进程里跑 git（openssl 后端 + 进程内 extraheader，凭证不落盘）。普通 `git status/log/diff` 不受影响。
- **交付**：成品先落 repo，再复制到工作区 `outputs/research-<日期>-<slug>/`，用文件卡片直接给伭奥；不让人去 GitHub 或 repo 目录里找。
- **定时**：2026-10-19 伭奥明确「暂时不用定时，需要时具体安排」。DSH 不挂任何研究定时；以后要加，先更新 `docs/routines.md` 再建。
- **权限**：本 repo 不加载 `.claude/settings.json` 之类的旧平台配置，也不声称其 deny 生效。DSH 下的权限按 `AGENTS.md` 第 6 节三档执行，由 Agent 严守。
- **联网**：研究依赖 `web_search` / `web_fetch`；遇到付费墙、登录墙、反爬时如实标「未打开」，不用搜索摘要冒充原文。

## 开工与恢复

1. 在工作区运行 `.\research\start-research.ps1`（联网同步加 `-Sync`，改脚本或换环境加 `-Test`）。脚本只读仓库：核对 origin、分支、提交、未提交改动，跑 `after_compact.py` 和 `topic_status.py`。
2. 完整读仓库 `AGENTS.md`、`memory/decisions.md`、`memory/judgment.md`、`memory/profile.md`、`memory/pending.md`、`memory/session-state.md`、`topics/index.md`、最新 `journal` 末尾。
3. 按当前课题读 `docs/method/`、`docs/formats/`、目标课题的 brief/plan/evidence/log。
4. 压缩前更新 `memory/session-state.md` 和课题 `log.md`；脚本不能恢复没落库的对话。

## 恢复失败时

缺文件、origin 不符、Python 不可用、GitHub 不可达：停下说明缺什么、影响哪一步。用本地副本时标日期和未同步风险；不编造「已读记忆」，不以连接器写入冒充 `git push`。
