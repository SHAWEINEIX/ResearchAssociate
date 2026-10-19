# 深度规格卡（docs/formats/）

> 每张卡是一种交付物的硬规格：长度、证据下限、必备章节、结论卡字段、禁用表达。`check_report.py` 会读卡里的 json 块做校验。卡末「本地规则」优先于通则。

## 怎么选卡

| 场景 | 用哪张 | 深度 |
|---|---|---|
| 查一个事实、一个数字、一个名单 | `quick-answer.md` | L0 |
| 支持一次汇报、一个判断，1–2 页 | `brief.md` | L1 |
| 要拍板、涉及钱或人、结论会被质疑 | `deep-report.md` | L2 |
| 3 个以上对象逐项比较 | `comparison.md` | L3 |
| 合作方、供应商、投资对象 | `due-diligence.md` | L4 |
| 政策、标准、监管变化 | `policy-brief.md` | L1/L2 |
| 已有课题的定期更新 | `watch-update.md` | 增量 |

## 卡里的 json 块

```json
{
  "key": "L1",
  "name": "简报",
  "max_chars": 1500,
  "min_chars": 400,
  "min_sources_total": 5,
  "min_sources_a": 3,
  "required_sections": ["结论卡", "关键发现", "待核", "来源"],
  "conclusion_card_fields": ["结论", "关键数字", "动作", "反证", "置信度"],
  "max_paragraph_lines": 5,
  "forbidden_patterns": ["综上所述", "由此可见", "赋能", "抓手", "闭环", "协同发力", "全面提升", "打造生态", "助力增长", "进一步", "不断", "切实", "扎实"]
}
```

- `min_sources_total` / `min_sources_a`：台账里 `已核` 的来源数；A 级单独计。
- `required_sections`：报告必须有的二级标题；脚本按 `## ` 标题匹配。
- `conclusion_card_fields`：结论卡里必须出现的字段名。
- `max_paragraph_lines`：连续非空行超过这个数报警告。
- `forbidden_patterns`：命中即不通过；引用原文时用引号包起来可豁免（脚本只对非引用行检查）。

## 通则

- 所有卡都要求：结论先行、数字带 `[E##]`、事实与判断分开、来源表可追。
- 所有卡都禁止：制作说明、「本文/本报告」、emoji、无出处的百分数。
- 超长先删重复与铺垫，不缩字硬塞；删完仍超，降档或拆成两份。
