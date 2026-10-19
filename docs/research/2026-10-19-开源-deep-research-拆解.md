# 调研存档 · 开源 deep research 拆解（2026-10-19）

> 建设期调研的原始摘要，供改方法时参考。接手研究课题时不读本文。链接与数字来自调研当时的页面，未逐条复核。

## 一、四个主力项目

### GPT Researcher
[repo](https://github.com/assafelovic/gpt-researcher)｜[deep research 文档](https://docs.gptr.dev/docs/gpt-researcher/gptr/deep_research)

- 循环：planner 拆问题 → 每问题一个 crawler → 逐来源摘要并记 URL → publisher 汇总；deep 模式树状递归（breadth=4 / depth=2 / concurrency=4）。
- 可借：来源级追踪；广度/深度/并发三旋钮即成本闸门；单分支失败不毁整轮。
- 产出：2000+ 词、20+ 来源 Markdown，编号引用 + 来源列表。
- 痛点：必须上 reasoning 模型；成本随时延爆炸；[引用不实讨论](https://github.com/assafelovic/gpt-researcher/discussions/1304)。

### LangChain open_deep_research
[repo](https://github.com/langchain-ai/open_deep_research)｜[configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py)

- 循环：澄清 → research brief → supervisor 用 think_tool / ConductResearch / ResearchComplete 决策（默认 6 轮、并行 5）→ 每个 researcher 是 ReAct（≤10 次工具调用）→ 压缩 → 一次性写终稿；>5 万字符网页先摘要。
- 可借：四模型分工；轮数/并行/调用全显式；checkpointer；子代理只回压缩稿。
- 痛点：[压缩阶段 token 超限删错消息](https://github.com/langchain-ai/open_deep_research/issues/252)。

### STORM / Co-STORM
[repo](https://github.com/stanford-oval/storm)｜[论文](https://arxiv.org/abs/2402.14207)

- 循环：先用同类条目发现「视角」→ 维基写手与专家多轮对话，专家只用 top-1 片段作答，查不到拒答 → 大纲 → 按节写作（信息表 URL 编号做引用）→ polish。
- 可借：视角引导提问扩覆盖；信息表让引用有据；mind map 压缩长对话。
- 痛点：官方承认「不能直接发表」；百科体例没有「所以呢」。

### Anthropic 多智能体研究系统
[blog](https://www.anthropic.com/engineering/multi-agent-research-system)

- 循环：lead agent 先写计划进 Memory → 并行 3–5 子代理、每个并行 3+ 工具 → 综合后决定是否再派 → CitationAgent 逐条定位引用。
- 可借：工作量分级写进 prompt；子代理产出落文件、只回引用；checkpoint + 错误恢复。
- 痛点（自述）：简单 query 派 50 个子代理；偏爱 SEO 农场；同步等待成瓶颈。

## 二、其他值得看

- [dzhng/deep-research](https://github.com/dzhng/deep-research)：状态只有 `learnings[] + visitedUrls[]`，天然可恢复；但正文断言无逐条归属，是反面教材。
- [Local Deep Research](https://github.com/LearningCircuit/local-deep-research)：来源质量一等公民（期刊声誉库、predatory 检测）；可追问。
- [nickscamara/open-deep-research](https://github.com/nickscamara/open-deep-research)：结构化「研究块 + 缺口」中间态比报告值钱。
- 中文：[通义 DeepResearch](https://github.com/Alibaba-NLP/DeepResearch)（ReAct 与 IterResearch；ReSum/WebWeaver/AgentFold）、[MindSearch](https://github.com/InternLM/MindSearch)（问题规划成 DAG）、[DeerFlow](https://github.com/bytedance/deer-flow)（skills/subagents/memory/上下文压缩）。

## 三、共性痛点

- 没有「so what」：[DRB](https://arxiv.org/abs/2506.11763) 把 insight 单列维度。
- 引用不实：DRB 的 FACT 专门量 citation accuracy；URL 堆文末最易被抓。
- 太长不可读：分节并行写作造成拼接感（[Lance Martin 复盘](https://rlancemartin.github.io/2025/07/30/bitter_lesson/)）。
- 成本/稳定性：breadth×depth 爆炸、15× token、压缩截断毁整轮。

## 四、15 个能力积木（本 repo 采纳情况）

| # | 积木 | 采纳 | 落在哪 |
|---|---|---|---|
| 1 | 澄清与简报 | 是 | `00-research-loop.md` 第 0 步、`brief.md` |
| 2 | 大纲分解 | 是 | `plan.md` 子问题 |
| 3 | 视角清单 | 是 | `01-question-design.md` 拆题 |
| 4 | 证据台账 | 是 | `evidence.md` |
| 5 | 引用契约 | 是 | `[E##]` + `check_report.py` |
| 6 | 研究日志 | 是 | `log.md` |
| 7 | 扇出并发 | 是 | `00` 预算与并行 |
| 8 | 上下文压缩 | 是 | 子 Agent 只回结论 + 证据行 |
| 9 | 预算与停止 | 是 | `00` 停止条件 |
| 10 | 分段写作 + 统一收口 | 是 | 研究收口后一次成文 |
| 11 | 洞察层 | 是 | 结论卡 + 反方与风险 |
| 12 | 质量门 | 是 | 红队 + `check_report.py` |
| 13 | 断点续跑 | 是 | 文件即状态 |
| 14 | 追问与再利用 | 是 | 课题目录 + 台账 |
| 15 | 来源质量 | 是 | `sources.md` + 分级 |

## 五、结论

- 先做证据台账 + 引用契约，再做并行扇出：前者定可信度，后者定成本。
- 不要边研究边写；研究收口后一次性写。
- 文件即状态：用目录与文件替代复杂运行时。
