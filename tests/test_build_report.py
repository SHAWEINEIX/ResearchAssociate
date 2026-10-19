#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_report 的测试：标题、结论卡、引用、表格、自包含。"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_report  # noqa: E402

SAMPLE = """# 测试题目

> 2026-10-19 · L1 简报 · 5 源

## 结论卡

- **结论**：A 类客户会形成采购高峰。
- **关键数字**：① 120 亿元 [E01]
- **动作**：① 10-24 前确认报价
- **反证**：若招标数低于 20 个 [E04]，则作废。
- **置信度**：中。

## 关键发现

### 1. 需求真实

正文里有引用 [E01]，还有 **加粗** 和 `代码` 和 [链接](https://example.com)。

| 维度 | 值 |
|---|---|
| 规模 | 120 亿元 [E01] |

## 待核

- 无。

## 来源

| 编号 | 机构 | URL |
|---|---|---|
| E01 | 甲机构 | https://example.com/a |
"""


class BuildReportTest(unittest.TestCase):
    def test_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "report-v1.md"
            md.write_text(SAMPLE, encoding="utf-8")
            out = Path(tmp) / "report-v1.html"
            html = build_report.build_html(md)
            out.write_text(html, encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("测试题目", html)
            self.assertIn('id="conclusion"', html)
            self.assertIn('class="cite">E01', html)
            self.assertIn("<table>", html)
            self.assertIn('href="https://example.com"', html)
            self.assertNotIn("{{", html)
            self.assertNotIn("本页内容", html)  # L1 不出目录

    def test_l2_has_toc(self):
        text = SAMPLE.replace("L1 简报", "L2 专题")
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "report-v1.md"
            md.write_text(text, encoding="utf-8")
            html = build_report.build_html(md)
            self.assertIn("本页内容", html)

    def test_extract_title_meta(self):
        title, meta, rest = build_report.extract_title_meta(SAMPLE.splitlines())
        self.assertEqual(title, "测试题目")
        self.assertIn("2026-10-19", meta)
        self.assertFalse(any(line.strip() == "# 测试题目" for line in rest))

    def test_without_card(self):
        md_text = "# 只有正文\n\n## 第一节\n\n一段话。\n"
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "report-v1.md"
            md.write_text(md_text, encoding="utf-8")
            html = build_report.build_html(md)
            self.assertNotIn('id="conclusion"', html)
            self.assertIn("第一节", html)


if __name__ == "__main__":
    unittest.main()
