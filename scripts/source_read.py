#!/usr/bin/env python3
"""只读读取邻居 Agent 仓库的指定文件。白名单，永不写入。

用法：
  python3 scripts/source_read.py list
  python3 scripts/source_read.py ticktick profile
  python3 scripts/source_read.py jobwork lines
  python3 scripts/source_read.py writer voice
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import research_common as rc


def workspace_root() -> Path:
    return Path(os.environ.get("RESEARCH_SOURCE_ROOT", str(rc.ROOT.parent))).expanduser()


def meeting_root() -> Path | None:
    explicit = os.environ.get("RESEARCH_MEETING_ROOT")
    if explicit:
        return Path(explicit).expanduser()
    config = workspace_root() / "meeting.local.json"
    if config.exists():
        try:
            data = json.loads(config.read_text(encoding="utf-8"))
            return Path(data["repo_root"]).expanduser()
        except (json.JSONDecodeError, KeyError, OSError):
            return None
    return None


def sources() -> dict[str, dict[str, Path]]:
    ws = workspace_root()
    mapping = {
        "ticktick": {
            "profile": ws / "ticktick" / "repo" / "memory" / "profile.md",
            "context": ws / "ticktick" / "repo" / "memory" / "context.md",
            "people": ws / "ticktick" / "repo" / "memory" / "people.md",
            "decisions": ws / "ticktick" / "repo" / "memory" / "decisions.md",
        },
        "jobwork": {
            "profile": ws / "jobwork" / "repo" / "memory" / "profile.md",
            "judgment": ws / "jobwork" / "repo" / "memory" / "judgment.md",
            "lines": ws / "jobwork" / "repo" / "lines" / "index.md",
        },
        "writer": {
            "context": ws / "writer" / "repo" / "memory" / "context.md",
            "people": ws / "writer" / "repo" / "memory" / "people.md",
            "voice": ws / "writer" / "repo" / "style" / "voice.md",
        },
    }
    meeting = meeting_root()
    if meeting:
        mapping["meeting"] = {
            "profile": meeting / "memory" / "profile.md",
            "people": meeting / "memory" / "people.md",
        }
    return mapping


def list_sources() -> int:
    print("可只读的邻居文件（业务只读，不写、不提交）：")
    for source, files in sources().items():
        print(f"\n{source}:")
        for name, path in files.items():
            state = "存在" if path.exists() else "缺失"
            print(f"  {name:<10} {path}  [{state}]")
    print("\n用法：python3 scripts/source_read.py <source> <name>")
    return 0


def main(argv=None) -> int:
    rc.setup_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help", "list"):
        return list_sources()
    if len(args) < 2:
        print("用法：python3 scripts/source_read.py <source> <name>；用 list 看可选项", file=sys.stderr)
        return 2
    source, name = args[0], args[1]
    table = sources()
    if source not in table:
        print(f"未知来源「{source}」；可用：{', '.join(table)}", file=sys.stderr)
        return 2
    if name not in table[source]:
        print(f"「{source}」没有「{name}」；可用：{', '.join(table[source])}", file=sys.stderr)
        return 2
    path = table[source][name]
    if not path.exists():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    print(f"<!-- 只读：{source}/{name} · {path} -->")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
