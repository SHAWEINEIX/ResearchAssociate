#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_report 的测试：格式、结论卡、引用、数字、套话、长度。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_report  # noqa: E402

EVIDENCE = """# 测试 · 证据台账

| 编号 | 断言 | 数值/原文 | 来源（机构·标题） | URL | 发布日 | 口径 | 级 | 状态 | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| E01 | 市场规模 | 120 亿元 | 甲机构·报告A | https://example.com/a | 2025-08-01 | 含企业培训 | A | 已核 |  |
| E02 | 增速 | 18% | 乙机构·报告B | https://example.com/b | 2025-09-01 | 同比 | A | 已核 |  |
| E03 | 客单价 | 2.8 万元 | 丙机构·报告C | https://example.com/c | 2025-06-01 | 企业采购 | A | 已核 |  |
| E04 | 招标数 | 20 个 | 丁机构·统计 | https://example.com/d | 2025-10-01 | 上海 | B | 已核 |  |
| E05 | 竞品价格 | 2–3 万元 | 戊机构·测评 | https://example.com/e | 2025-07-01 | 公开报价 | B | 已核 |  |
"""

REPORT = """# 测试题目

> 2026-10-19 · L1 简报 · 5 源 · 置信度中

## 结论卡

- **结论**：A 类客户会在 2026 年第四季度形成采购高峰。
- **关键数字**：① 市场规模 120 亿元 [E01] ② 增速 18% [E02] ③ 客单价 2.8 万元 [E03]
- **动作**：① 在 2026-10-24 前确认报价 ② 11 月前接触三家客户 ③ 12 月前完成交付
- **反证**：若 2026 年第四季度招标数低于 20 个 [E04]，则本结论作废。
- **置信度**：中 —— 因为缺一手采购数据。

## 关键发现

### 1. A 类客户付费意愿高

A 类客户的预算已经落到具体场景，采购周期比预期短。市场规模 120 亿元 [E01]，增速 18% [E02]。

### 2. B 类客户仍在观望

B 类客户对效果存疑，决策链条更长，今年更可能做小范围试点。

### 3. 竞品定价集中在 2–3 万元

公开报价集中在 2–3 万元 [E05]，低于我们原定价格，需要重新核算交付成本。

## 待核

- 2025 年企业采购总额未获取。

## 来源

| 编号 | 机构 | 标题 | 发布日 | URL |
|---|---|---|---|---|
| E01 | 甲机构 | 报告A | 2025-08-01 | https://example.com/a |
| E02 | 乙机构 | 报告B | 2025-09-01 | https://example.com/b |
| E03 | 丙机构 | 报告C | 2025-06-01 | https://example.com/c |
| E04 | 丁机构 | 统计 | 2025-10-01 | https://example.com/d |
| E05 | 戊机构 | 测评 | 2025-07-01 | https://example.com/e |
"""


def make_topic(tmp: Path, report: str = REPORT, evidence: str = EVIDENCE) -> Path:
    topic = tmp / "2026-10-19-test-topic"
    topic.mkdir(parents=True)
    (topic / "evidence.md").write_text(evidence, encoding="utf-8")
    brief = topic / "brief.md"
    brief.write_text("# 测试题目\n\n> 深度：L1\n", encoding="utf-8")
    path = topic / "report-v1.md"
    path.write_text(report, encoding="utf-8")
    return path


def errors(result):
    return [f for f in result["findings"] if f["level"] == "error"]


class CheckReportTest(unittest.TestCase):
    def test_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp))
            result = check_report.run(path, "L1")
            self.assertEqual(errors(result), [])

    def test_missing_citation_fails(self):
        report = REPORT.replace("市场规模 120 亿元 [E01]", "市场规模 120 亿元")
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), report)
            result = check_report.run(path, "L1", strict=True)
            self.assertTrue(any("数字出处" in f["check"] for f in errors(result)))

    def test_unknown_ref_fails(self):
        report = REPORT + "\n补充：另一个数字 30 亿元 [E99]。\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), report)
            result = check_report.run(path, "L1")
            self.assertTrue(any("不存在" in f["message"] for f in errors(result)))

    def test_forbidden_phrase_fails(self):
        report = REPORT.replace("## 待核", "综上所述，情况就是这样。\n\n## 待核")
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), report)
            result = check_report.run(path, "L1")
            self.assertTrue(any("综上所述" in f["message"] for f in errors(result)))

    def test_missing_section_fails(self):
        report = REPORT.replace("## 待核", "## 其他")
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), report)
            result = check_report.run(path, "L1")
            self.assertTrue(any("待核" in f["message"] for f in errors(result)))

    def test_too_long_fails(self):
        filler = "\n\n" + "这是一段用于测试长度的普通文字，不包含数字和套话。" * 60
        report = REPORT.replace("## 待核", filler + "\n\n## 待核")
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), report)
            result = check_report.run(path, "L1")
            self.assertTrue(any(f["check"] == "长度" for f in errors(result)))

    def test_few_sources_fails(self):
        evidence = EVIDENCE.splitlines()[0:6]
        with tempfile.TemporaryDirectory() as tmp:
            path = make_topic(Path(tmp), evidence="\n".join(evidence) + "\n")
            result = check_report.run(path, "L1")
            self.assertTrue(any(f["check"] == "证据量" for f in errors(result)))


if __name__ == "__main__":
    unittest.main()
