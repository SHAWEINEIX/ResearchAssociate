#!/usr/bin/env python3
"""接手、压缩、换会话时手动补回本仓库状态；只读，不依赖平台钩子。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import research_common as rc

SECTIONS = [
    ("memory/session-state.md", 2500),
    ("memory/decisions.md", 7000),
    ("memory/judgment.md", 5000),
    ("memory/profile.md", 3500),
    ("memory/pending.md", 2000),
    ("topics/index.md", 4500),
]
LIMIT = 32000


def bound(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    marker = "\n（中段未载入，按需读完整文件；以下为最新条目）\n"
    room = max(limit - len(marker), 0)
    front = room // 3
    return text[:front] + marker + text[-(room - front):]


def git_state() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(rc.ROOT), "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode:
            return "git 状态：未知"
        return f"未提交的改动：\n{result.stdout.strip()}" if result.stdout.strip() else "未提交的改动：无"
    except (OSError, subprocess.SubprocessError):
        return "git 状态：未知"


def journal_tail(n: int = 12) -> str:
    files = sorted((rc.ROOT / "journal").glob("*.md"))
    if not files:
        return "（没有日志）"
    try:
        lines = files[-1].read_text(encoding="utf-8").rstrip().splitlines()
        return files[-1].name + "\n" + "\n".join(lines[-n:])
    except OSError:
        return "（读取日志失败）"


def build() -> str:
    parts = [
        "[接手补回] 本 repo 是规则、记忆、课题和脚本的唯一来源；先读 AGENTS.md，平台读 DSH.md。",
        "## 执行边界\n研究助理；其他 Agent 仓库只读；不对外发送；不挂定时。",
    ]
    for rel, budget in SECTIONS:
        path = rc.ROOT / rel
        text = path.read_text(encoding="utf-8").strip() if path.exists() else f"（缺文件：{rel}）"
        parts.append(f"## {rel}\n" + bound(text, budget))
    parts.append("## git\n" + bound(git_state(), 1200))
    parts.append("## journal 末尾\n" + bound(journal_tail(), 1600))
    return "\n\n".join(parts)[:LIMIT]


if __name__ == "__main__":
    rc.setup_stdio()
    try:
        print(build())
    except Exception as exc:  # 恢复失败也要明确报出来
        print(f"[接手补回] 读取失败：{exc}")
