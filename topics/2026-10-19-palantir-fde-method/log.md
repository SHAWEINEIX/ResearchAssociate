# Palantir FDE 方法论与 Echo/Delta 框架 · 过程记录

> 每一步一行：做了什么、得出什么、下一步。中断恢复先看这里末尾。

## 立项 2026-10-19

- 伭奥的原话：「关于 palantir、FDE 方法轮，包括 echo delta 等概念和框架。深度研究。我需要非常深度的了解整概念、框架、做法和方法论。应用到我的房地产行业 X AI 的培训研究之中。」
- 深度：L2（他已说「深度研究」，不再问；按 L2 专题做，4000–8000 字、15–30 源、红队）。
- 用途与读者：改造 FDE 高级培训班与 AI 技能班；读者是伭奥，可能转李琛/周总。
- 待问：FDE 班是否就是 Forward Deployed Engineer；首期企业班还是个人班；三家房企场景。默认按「同名同源、企业班」处理。

## 研究过程

- 第 1 轮：搜 Palantir FDE、Echo/Delta/FDPM、a16z、华西证券、腾讯云、YC、Pragmatic Engineer；确认 Echo=Deployment Strategist、Delta=FDSE、Dev=平台工程师，FDPM 只见于中文二手。
- 第 2 轮：读 Palantir 官方 Dev vs Delta、FDSE/Deployment Strategist JD、Ontology/AIP/AI FDE/Evals 文档；确认官方一手定义与 AI FDE 产品化。
- 第 3 轮：读 YC Bob McGrew 访谈、Pragmatic Engineer、腾讯云 Colin Jarvis 方法文、FDE-Wiki 方法论/能力/沙盘/知识转移章节；补齐四道工序与培训设计。
- 第 4 轮：读国家统计局 2025 房地产数据、腾讯云 WorkBuddy FDE 精英班、中培伟业 FDE 特训营；确认房地产约束与国内竞品形态。
- 证据台账：28 条，A 级 9；C 级集中在 FDE-Wiki、53AI、Hayat Amin，已在正文标注「本次可见」「待核」。
- 概念修正：原以为「Echo-Delta」是一套公开框架，实际是内部编队名；FDPM 未在 Palantir 公开岗位独立出现，降为「项目推进职能」。
- 报告 v1：8882 字，结论卡 + 5 条关键发现 + 7 节正文 + 反方 + 待核 + 来源。
- 红队：独立定向复核返回三条反驳（平台归因、分轨与 pairing 矛盾、数字不承载推理），已逐条处理：结论改为「可验收交付单元」、补适用条件与反方五、首期收缩为一家房企一个场景、三轨八周降为待验证。完整 A–E 清单由主 Agent 自评，记 `red-team-v1.md`。
- 自检：`check_report.py` 通过；HTML 生成并在 390px 宽度检查，目录折叠。

## 交付

- 报告版本：`report-v1.md`
- HTML：`report-v1.html`
- 红队：`red-team-v1.md`（待）
- 伭奥的反馈：待
- 后续：按红队修订 v2；首期企业班方案另出执行版。

## 更正

- （暂无）
