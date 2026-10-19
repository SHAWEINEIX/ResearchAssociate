#!/usr/bin/env python3
"""建课题：创建 topics/<日期>-<slug>/ 的 brief/plan/evidence/log，并列出相似旧题。"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

import research_common as rc


def slugify(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    slug = "-".join(w.lower() for w in words)
    if len(slug) < 3:
        slug = "topic-" + hashlib.sha1(title.encode("utf-8")).hexdigest()[:6]
    return slug[:60].strip("-")


def similar_topics(title: str) -> list[tuple[float, str, str]]:
    found = []
    for topic in rc.topic_dirs():
        brief = rc.parse_brief(topic / "brief.md")
        other = brief.get("title", topic.name)
        ratio = SequenceMatcher(None, title, other).ratio()
        if ratio >= 0.35:
            found.append((round(ratio, 2), other, topic.name))
    return sorted(found, reverse=True)[:5]


def main(argv=None) -> int:
    rc.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("title", help="课题题目（中文即可）")
    ap.add_argument("--slug", help="目录用的英文短名；不给则从题目里的英文词生成")
    ap.add_argument("--depth", default="L1", choices=["L0", "L1", "L2", "L3", "L4"],
                    help="深度档，默认 L1（新课题应先问伭奥）")
    ap.add_argument("--date", default=date.today().isoformat(), help="立项日期 YYYY-MM-DD")
    ap.add_argument("--force", action="store_true", help="目录已存在时仍继续（会覆盖模板文件）")
    args = ap.parse_args(argv)

    slug = args.slug or slugify(args.title)
    name = f"{args.date}-{slug}"
    topic = rc.TOPICS_DIR / name

    similar = similar_topics(args.title)
    if similar:
        print("相似旧题（先确认是不是同一件）：")
        for ratio, other, folder in similar:
            print(f"  {ratio:.2f}  {other}  ·  topics/{folder}/")
        print()

    if topic.exists() and not args.force:
        print(f"课题已存在：{rc.rel(topic)}（用 --force 覆盖模板）", file=sys.stderr)
        return 1

    topic.mkdir(parents=True, exist_ok=True)
    replacements = {"{{TITLE}}": args.title, "{{DATE}}": args.date, "{{DEPTH}}": args.depth}
    created = []
    for template_name, output_name in (
        ("brief.md", "brief.md"),
        ("plan.md", "plan.md"),
        ("evidence.md", "evidence.md"),
        ("topic-log.md", "log.md"),
    ):
        template = rc.read(rc.TEMPLATES_DIR / template_name)
        for key, value in replacements.items():
            template = template.replace(key, value)
        target = topic / output_name
        rc.write(target, template)
        created.append(rc.rel(target))

    rc.update_index()

    print(f"已建课题：{rc.rel(topic)}  （{args.depth}）")
    for path in created:
        print(f"  {path}")
    print(f"  台账已更新：{rc.rel(rc.INDEX_PATH)}")
    if args.depth == "L0":
        print("提示：L0 快答通常不建课题，确认需要留档再继续。")
    print("下一步：填 brief.md（用途、读者、成功标准），再写 plan.md 的子问题与信源配方。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
