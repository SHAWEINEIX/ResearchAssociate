# 当前会话最小交接状态

更新：2026-10-19（周一）· 建设完成，等第一个课题 · 平台 DSH

## 当前请求与完成状态

- 2026-10-19：从零建设研究助理，repo `SHAWEINEIX/ResearchAssociate`。已完成：契约、平台入口、记忆 9 份、方法 7 篇、规格卡 6 张、模板 8 份、脚本 6 个、测试 15 项、格式演示（Markdown + HTML）。
- 伭奥已确认：用途四类、领域五类、交付形态（结论卡 + Markdown + HTML）、深度每次先问并给推荐档、暂不设定时。

## 当前入口

- 工作区 `research/`，仓库 `research/repo`。
- 开工：`.\research\start-research.ps1`（联网 `-Sync`，测试 `-Test`）；恢复：`python3 scripts/after_compact.py`。
- 课题台账：`topics/index.md`（当前为空，等第一个课题）。
- 格式演示：`examples/format-demo.md` 与 `examples/format-demo.html`（数字为虚构，仅看版式）。

## 已验证

- 15 项 unittest 通过（check_report 7、build_report 4、new_topic 4）。
- `new_topic.py` 建题 + 台账更新、`topic_status.py` 扫描、`check_report.py` 校验、`build_report.py` 渲染、`after_compact.py` 恢复均实跑过。
- HTML 在 390px 宽度下检查过：标题换行、结论卡、表格自动换行、无横向溢出；L1 不显示目录，L2 显示。
- `start-research.ps1` 实跑通过；git 联网用 `research/git-env.ps1`。

## 未决与下一步

- 等伭奥的第一个真实研究题目；接题先问深度（D-002）。
- 待观察：HTML 版式是否合口味；是否需要图表；英文一手来源使用频率；真实网页抓取的付费墙与反爬边界（首次课题时实测并记 `docs/实测记录.md`）。
- 待办：第一次真实交付后，按 D-019 开始记试用期指标。
