#!/usr/bin/env python3
"""课题台账：列状态、证据数、过期；可重算 topics/index.md 的表格。"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

import research_common as rc


def days_since(iso: str) -> int | None:
    if not iso:
        return None
    try:
        return (date.today() - datetime.strptime(iso, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def collect() -> list[dict]:
    existing = {}
    if rc.INDEX_PATH.exists():
        existing = rc.parse_index_rows(rc.read(rc.INDEX_PATH))
    items = []
    for topic in rc.topic_dirs():
        brief = rc.parse_brief(topic / "brief.md")
        rows = rc.parse_evidence(rc.read(topic / "evidence.md")) if (topic / "evidence.md").exists() else []
        counts = rc.count_evidence(rows)
        report = rc.latest_report(topic)
        old = existing.get(topic.name)
        updated = rc.latest_mtime(topic)
        items.append({
            "slug": topic.name,
            "title": brief.get("title", topic.name),
            "depth": brief.get("depth", ""),
            "status": old[3] if old and len(old) > 3 and old[3] else (brief.get("status") or "研究中"),
            "next": old[4] if old and len(old) > 4 and old[4] else "待填",
            "updated": updated,
            "days": days_since(updated),
            "evidence": counts,
            "report": rc.rel(report) if report else "",
            "entry": f"topics/{topic.name}/",
        })
    return sorted(items, key=lambda x: x["updated"], reverse=True)


def main(argv=None) -> int:
    rc.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-index", action="store_true", help="重算 topics/index.md 的 AUTO 区块")
    ap.add_argument("--stale", type=int, default=14, help="超过多少天未更新算过期，默认 14")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    items = collect()
    if args.write_index:
        rc.update_index()
        print(f"已重算台账：{rc.rel(rc.INDEX_PATH)}（{len(items)} 个课题）")

    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0

    if not items:
        print("暂无课题。用 new_topic.py 建第一个。")
        return 0

    print(f"{'题号':<40} {'深度':<4} {'状态':<6} {'证据':<10} {'报告':<6} {'更新':<10} 下一步")
    stale_count = 0
    for item in items:
        ev = item["evidence"]
        ev_text = f"{ev['total']}/A{ev['A']}"
        report = "有" if item["report"] else "—"
        updated = item["updated"] or "—"
        days = item["days"]
        stale = days is not None and days > args.stale and item["status"] not in ("已交付", "已归档", "示例")
        if stale:
            stale_count += 1
            updated += f"（{days}天）"
        print(f"{item['slug']:<40} {item['depth']:<4} {item['status']:<6} {ev_text:<10} {report:<6} {updated:<10} {item['next']}")
    if stale_count:
        print(f"\n提醒：{stale_count} 个课题超过 {args.stale} 天未更新。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
