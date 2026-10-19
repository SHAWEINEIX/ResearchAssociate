#!/usr/bin/env python3
"""交付前校验：格式卡、结论卡、引用完整性、数字出处、套话、长度、段落。

退出码：0 通过（可有提醒）、1 有不通过、2 用法或文件错误。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import research_common as rc

REQUIRED_DEFAULT = ["结论卡", "关键发现", "待核", "来源"]


class Finding:
    def __init__(self, level: str, check: str, message: str):
        self.level = level  # error / warn
        self.check = check
        self.message = message

    def as_dict(self):
        return {"level": self.level, "check": self.check, "message": self.message}


def add(findings, level, check, message):
    findings.append(Finding(level, check, message))


def check_sections(text, card, findings):
    titles = rc.section_titles(text, 2)
    required = card.get("required_sections") or REQUIRED_DEFAULT
    for name in required:
        if not any(name in t for t in titles):
            add(findings, "error", "章节", f"缺少必备章节「## {name}」")
    order = [i for i, t in enumerate(titles) if "结论卡" in t]
    found = [i for i, t in enumerate(titles) if "关键发现" in t]
    if order and found and order[0] > found[0]:
        add(findings, "warn", "章节", "「结论卡」应排在「关键发现」之前")


def check_conclusion_card(text, card, findings):
    fields = card.get("conclusion_card_fields") or []
    if not fields:
        return
    section = rc.get_section(text, "结论卡")
    if not section:
        add(findings, "error", "结论卡", "找不到「## 结论卡」内容")
        return
    for field in fields:
        if field not in section:
            add(findings, "error", "结论卡", f"结论卡缺少字段「{field}」")
    if "结论" in section:
        line = next((l for l in section.splitlines() if "结论" in l), "")
        hedges = ["可能", "或许", "有待观察", "机遇与挑战", "情况复杂"]
        for word in hedges:
            if word in line and "反证" not in line:
                add(findings, "warn", "结论卡", f"结论句出现模糊词「{word}」：{line.strip()[:60]}")
                break


def check_citations(text, rows, findings, allow_missing_evidence=False):
    if not rows:
        if not allow_missing_evidence:
            add(findings, "error", "证据", "找不到 evidence.md 台账（或台账为空）；用 --no-evidence 跳过")
        return
    by_id = {row.get("id", ""): row for row in rows}
    refs = rc.refs_in(text)
    if not refs and not allow_missing_evidence:
        add(findings, "error", "证据", "正文没有任何 [E##] 引用")
    for ref in sorted(refs):
        row = by_id.get(ref)
        if not row:
            add(findings, "error", "引用", f"正文引用 [{ref}] 在台账中不存在")
            continue
        if "作废" in row.get("status", ""):
            add(findings, "error", "引用", f"[{ref}] 状态为作废，不能引用")
        if "未打开" in row.get("status", ""):
            add(findings, "error", "引用", f"[{ref}] 状态为未打开，不能引用")
        if not row.get("url", "").startswith("http"):
            add(findings, "error", "引用", f"[{ref}] 缺少有效 URL")
        if not row.get("date", ""):
            add(findings, "warn", "引用", f"[{ref}] 缺少发布日")
        if not row.get("scope", ""):
            add(findings, "warn", "引用", f"[{ref}] 缺少口径")
        if "待核" in row.get("status", "") or "冲突" in row.get("status", ""):
            add(findings, "warn", "引用", f"[{ref}] 状态为「{row.get('status')}」，正文需标明")
    return refs


def check_evidence_sufficiency(rows, card, findings, allow_few=False):
    counts = rc.count_evidence(rows)
    min_total = int(card.get("min_sources_total") or 0)
    min_a = int(card.get("min_sources_a") or 0)
    if min_total and counts["total"] < min_total and not allow_few:
        add(findings, "error", "证据量", f"台账 {counts['total']} 条，低于本档要求 {min_total} 条")
    if min_a and counts["A"] < min_a and not allow_few:
        add(findings, "error", "证据量", f"A 级 {counts['A']} 条，低于本档要求 {min_a} 条")
    return counts


def check_numbers(text, findings, strict=False):
    level = "error" if strict else "warn"
    in_sources = False
    lines = text.splitlines()
    in_code = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith("## "):
            in_sources = ("来源" in line) or ("待核" in line)
        if in_sources:
            continue
        if line.strip().startswith("|") and set(line.strip()) <= {"|", "-", ":", " "}:
            continue
        if "动作" in line and ("：" in line or ":" in line):
            # 动作里的数量是执行安排，不是事实断言
            continue
        tokens = rc.numeric_tokens(line)
        if not tokens or rc.has_citation(line):
            continue
        if any(marker in line for marker in ("未获取", "待核", "推测", "估算", "未说明", "未披露")):
            continue
        add(findings, level, "数字出处", f"第 {i} 行有数字但无 [E##]：{tokens[:3]} · {line.strip()[:60]}")


def check_forbidden(text, card, findings):
    patterns = list(dict.fromkeys(rc.DEFAULT_FORBIDDEN + list(card.get("forbidden_patterns") or [])))
    in_code = False
    in_quote_block = False
    hits = 0
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith(">"):
            in_quote_block = True
            continue
        body = rc.strip_quoted(line)
        for pattern in patterns:
            if pattern in body:
                hits += 1
                if hits <= 12:
                    add(findings, "error", "套话", f"第 {i} 行出现禁用表达「{pattern}」")
    if hits > 12:
        add(findings, "error", "套话", f"禁用表达共 {hits} 处（只列出前 12 处）")


def check_length(text, card, findings):
    count = rc.prose_char_count(text)
    max_chars = int(card.get("max_chars") or 0)
    min_chars = int(card.get("min_chars") or 0)
    if max_chars and count > max_chars:
        add(findings, "error", "长度", f"约 {count} 字，超出本档上限 {max_chars} 字；先删重复与铺垫")
    if min_chars and count < min_chars:
        add(findings, "warn", "长度", f"约 {count} 字，低于本档下限 {min_chars} 字")
    return count


def check_paragraphs(text, card, findings):
    max_lines = int(card.get("max_paragraph_lines") or 5)
    for start, count in rc.paragraph_line_runs(text):
        if count > max_lines:
            add(findings, "warn", "段落", f"第 {start} 行起连续 {count} 行未分段（上限 {max_lines}）")


def check_sources_section(text, findings):
    section = rc.get_section(text, "来源")
    if not section:
        add(findings, "error", "来源", "缺少「## 来源」或内容为空")
        return
    if not rc.refs_in(section) and "| E" not in section and "E01" not in section:
        add(findings, "warn", "来源", "来源章节没有 E 编号")


def run(report_path: Path, format_key=None, strict=False, allow_few=False, no_evidence=False):
    findings: list[Finding] = []
    if not report_path.exists():
        raise FileNotFoundError(f"报告不存在：{report_path}")
    text = rc.read(report_path)
    card = rc.infer_card(report_path, format_key)
    if not card:
        add(findings, "warn", "格式", "没有识别到格式卡；按默认 L1 规则检查（可用 --format 指定）")
        card = {"key": "L1", "name": "简报", "required_sections": REQUIRED_DEFAULT,
                "conclusion_card_fields": ["结论", "关键数字", "动作", "反证", "置信度"],
                "max_chars": 1500, "min_chars": 400, "min_sources_total": 5, "min_sources_a": 3,
                "max_paragraph_lines": 5, "forbidden_patterns": []}

    check_sections(text, card, findings)
    check_conclusion_card(text, card, findings)
    rows = [] if no_evidence else rc.load_evidence(report_path)
    check_citations(text, rows, findings, allow_missing_evidence=no_evidence)
    counts = check_evidence_sufficiency(rows, card, findings, allow_few=allow_few or no_evidence)
    check_numbers(text, findings, strict=strict)
    check_forbidden(text, card, findings)
    chars = check_length(text, card, findings)
    check_paragraphs(text, card, findings)
    check_sources_section(text, findings)

    return {
        "report": str(report_path),
        "card": card.get("key"),
        "chars": chars,
        "evidence": counts,
        "findings": [f.as_dict() for f in findings],
    }


def main(argv=None) -> int:
    rc.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", help="报告 Markdown 路径")
    ap.add_argument("--format", dest="format_key", help="格式卡 key（L0/L1/L2/L3/L4/L1-P/WATCH）")
    ap.add_argument("--strict", action="store_true", help="数字无出处按错误处理")
    ap.add_argument("--allow-few-sources", action="store_true", help="证据量不足只警告")
    ap.add_argument("--no-evidence", action="store_true", help="跳过证据台账检查")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    try:
        result = run(Path(args.report), args.format_key, args.strict,
                     args.allow_few_sources, args.no_evidence)
    except FileNotFoundError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    errors = [f for f in result["findings"] if f["level"] == "error"]
    warns = [f for f in result["findings"] if f["level"] == "warn"]

    if args.json:
        result["ok"] = not errors
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not errors else 1

    print(f"报告：{result['report']}")
    print(f"格式：{result['card'] or '未识别'} · 约 {result['chars']} 字 · "
          f"台账 {result['evidence']['total']} 条（A {result['evidence']['A']}）")
    if errors:
        print("\n不通过：")
        for item in errors:
            print(f"  ✗ [{item['check']}] {item['message']}")
    if warns:
        print("\n提醒：")
        for item in warns:
            print(f"  ! [{item['check']}] {item['message']}")
    if not errors and not warns:
        print("\n通过：格式、结论卡、引用、数字、长度、段落都没有问题。")
    elif not errors:
        print(f"\n通过（有 {len(warns)} 条提醒）。")
    else:
        print(f"\n未通过（{len(errors)} 条不通过，{len(warns)} 条提醒）。")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
