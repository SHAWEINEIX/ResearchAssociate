# 当前会话最小交接状态

更新：2026-10-19（周一）· 首个真实课题待交付 · 平台 DSH

## 当前请求与完成状态

- 伭奥要求深度研究 Palantir FDE 方法论、Echo/Delta 等概念与框架，并应用到房地产行业 AI 培训。
- 课题 `topics/2026-10-19-palantir-fde-method/`（L2）已完成：brief、plan、evidence（28 条，A 级 9）、report-v1（8882 字）、HTML、red-team-v1。
- 结论：FDE 是「编队 + 工序」，不是驻场外包；房地产 AI 培训以「一个可验收的交付单元」为教学单位，三轨八周、客户签字验收。置信度中。
- 红队：独立定向复核三条意见（平台归因、分轨与 pairing 矛盾、数字不承载推理）已逐条处理；完整 A–E 清单自评，见 `red-team-v1.md`。

## 当前入口

- 工作区 `research/`，仓库 `research/repo`。
- 开工：`.\research\start-research.ps1`；恢复：`python3 scripts/after_compact.py`。
- 课题台账：`topics/index.md`；本课题：`topics/2026-10-19-palantir-fde-method/`。

## 已验证

- 15 项 unittest 通过；report-v1 通过 `check_report.py`（L2，28 条证据，A 9，8882 字）。
- HTML 生成；桌面与 390px 手机宽度检查，目录折叠，表格不裂词。
- 证据逐条可追到 `evidence.md`；C 级来源已在正文标注。

## 未决与下一步

- 把结论卡 + HTML 用文件卡片发给伭奥；等他答：FDE 班是否就是 Forward Deployed Engineer；首期企业班还是个人班；哪一家房企、哪一个场景。
- 下一步：按他的选择出首期执行版（交付单元标准、沙盘剧本、评分表、招生页）。
- 待观察：真实网页抓取的付费墙边界（已记 `docs/实测记录.md`）；首次真实交付后按 D-019 记试用期指标。
