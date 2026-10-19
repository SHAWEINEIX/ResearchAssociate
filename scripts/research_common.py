#!/usr/bin/env python3
"""研究助理共享工具：格式卡、证据台账、课题目录、台账索引。只用标准库。"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMATS_DIR = ROOT / "docs" / "formats"
TEMPLATES_DIR = ROOT / "docs" / "templates"
TOPICS_DIR = ROOT / "topics"
INDEX_PATH = TOPICS_DIR / "index.md"

AUTO_BEGIN = "<!-- AUTO:TOPICS:BEGIN -->"
AUTO_END = "<!-- AUTO:TOPICS:END -->"

DEFAULT_FORBIDDEN = [
    "综上所述", "由此可见", "值得注意的是", "赋能", "抓手", "闭环",
    "协同发力", "全面提升", "打造生态", "助力增长", "进一步", "不断",
    "切实", "扎实", "本文", "本报告", "接下来将", "分为三部分",
]


def setup_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def cjk_count(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def prose_char_count(text: str) -> int:
    """粗略字数：去掉代码块、markdown 符号与空白后计数。"""
    body = strip_code_blocks(text)
    body = re.sub(r"`[^`]*`", "", body)
    body = re.sub(r"[#>*_|\[\]()`~-]+", "", body)
    body = re.sub(r"\s+", "", body)
    return len(body)


def strip_quoted(text: str) -> str:
    return re.sub(r"「[^」]*」|“[^”]*”|\"[^\"]*\"", "", text)


# ---------- 格式卡 ----------

def load_cards() -> dict:
    cards = {}
    if not FORMATS_DIR.exists():
        return cards
    for path in sorted(FORMATS_DIR.glob("*.md")):
        match = re.search(r"```json\s*(.*?)```", read(path), flags=re.S)
        if not match:
            continue
        try:
            card = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        card["path"] = rel(path)
        cards[str(card.get("key", path.stem))] = card
    return cards


DEPTH_TO_KEY = {"L0": "L0", "L1": "L1", "L2": "L2", "L3": "L3", "L4": "L4"}


def infer_card(report_path: Path, override: str | None = None) -> dict | None:
    cards = load_cards()
    if override:
        if override in cards:
            return cards[override]
        for key, card in cards.items():
            if override in (key, str(card.get("name", ""))):
                return card
        return None
    text = read(report_path)[:1200]
    match = re.search(r"\bL([0-4])\b", text)
    depth = f"L{match.group(1)}" if match else None
    if not depth:
        brief = Path(report_path).parent / "brief.md"
        if brief.exists():
            m2 = re.search(r"深度[：:]\s*(L[0-4])", read(brief))
            depth = m2.group(1) if m2 else None
    if depth:
        return cards.get(DEPTH_TO_KEY.get(depth, depth))
    return None


# ---------- Markdown 结构 ----------

HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def headings(text: str) -> list[tuple[int, str, int]]:
    out = []
    in_code = False
    for i, line in enumerate(text.splitlines()):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADING_RE.match(line)
        if m:
            out.append((len(m.group(1)), m.group(2).strip(), i))
    return out


def get_section(text: str, name: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= 2 and name in m.group(2):
            start = i + 1
            break
    if start is None:
        return ""
    out = []
    in_code = False
    for line in lines[start:]:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code:
            m = HEADING_RE.match(line)
            if m and len(m.group(1)) <= 2:
                break
        out.append(line)
    return "\n".join(out).strip()


def section_titles(text: str, level: int = 2) -> list[str]:
    return [t for lv, t, _ in headings(text) if lv == level]


# ---------- 证据台账 ----------

def split_cells(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def norm_header(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


COLUMN_ALIASES = {
    "id": ("编号", "id", "序号"),
    "claim": ("断言", "事实", "claim", "结论"),
    "value": ("数值/原文", "数值", "原文", "数据"),
    "source": ("来源", "机构", "source"),
    "url": ("url", "链接"),
    "date": ("发布日", "日期", "时间"),
    "scope": ("口径", "统计口径"),
    "grade": ("级", "等级", "grade"),
    "status": ("状态", "status"),
    "note": ("备注", "note"),
}


def map_columns(headers: list[str]) -> dict:
    mapping = {}
    normalized = [norm_header(h) for h in headers]
    for key, aliases in COLUMN_ALIASES.items():
        for idx, head in enumerate(normalized):
            if any(norm_header(alias) in head for alias in aliases):
                mapping[key] = idx
                break
    return mapping


def parse_evidence(text: str) -> list[dict]:
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "编号" in line:
            header_idx = i
            break
    if header_idx is None:
        return []
    headers = split_cells(lines[header_idx])
    mapping = map_columns(headers)
    rows = []
    for i in range(header_idx + 2, len(lines)):
        line = lines[i]
        if not line.strip().startswith("|"):
            break
        cells = split_cells(line)
        if not cells or not cells[0] or set(cells[0]) <= {"-", ":"}:
            continue
        row = {"line": i + 1}
        for key, idx in mapping.items():
            row[key] = cells[idx] if idx < len(cells) else ""
        if "id" not in row:
            row["id"] = cells[0]
        row["id"] = row["id"].upper()
        rows.append(row)
    return rows


def load_evidence(report_path: Path) -> list[dict]:
    evidence = Path(report_path).parent / "evidence.md"
    if not evidence.exists():
        return []
    return parse_evidence(read(evidence))


REF_RE = re.compile(r"\[E(\d{2,})\]")


def refs_in(text: str) -> set[str]:
    return {f"E{m.group(1)}" for m in REF_RE.finditer(text)}


def has_citation(line: str) -> bool:
    return bool(REF_RE.search(line))


# ---------- 数字与段落 ----------

NUMBER_RE = re.compile(
    r"\d[\d,.]*\s*(%|％|亿元|万元|亿|万|倍|家|人|个|台|次|天|个月|元|美元|港元)"
)


def numeric_tokens(line: str) -> list[str]:
    clean = REF_RE.sub("", line)
    clean = re.sub(r"https?://\S+", "", clean)
    clean = re.sub(r"(19|20)\d{2}\s*年", "", clean)
    clean = re.sub(r"(19|20)\d{2}[-/.]\d{1,2}([-/.]\d{1,2})?", "", clean)
    clean = re.sub(r"第\s*\d+\s*[章节条]", "", clean)
    clean = re.sub(r"E\d{2,}", "", clean)
    return [m.group(0) for m in NUMBER_RE.finditer(clean)]


def paragraph_line_runs(text: str) -> list[tuple[int, int]]:
    """返回 (起始行号, 连续非空段落行数)，只看正文段落。"""
    runs = []
    count = 0
    start = 0
    in_code = False
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if count:
                runs.append((start, count))
            count = 0
            continue
        if in_code:
            continue
        is_plain = stripped and not stripped.startswith(("#", "|", ">", "-", "*", "`", "<!--"))
        if is_plain:
            if count == 0:
                start = i
            count += 1
        else:
            if count:
                runs.append((start, count))
            count = 0
    if count:
        runs.append((start, count))
    return runs


# ---------- 课题 ----------

def topic_dirs() -> list[Path]:
    if not TOPICS_DIR.exists():
        return []
    return sorted(
        p for p in TOPICS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name != "_template"
    )


def topic_dir_for(path: Path) -> Path | None:
    path = Path(path)
    for candidate in (path.parent, path.parent.parent):
        if (candidate / "evidence.md").exists() or (candidate / "brief.md").exists():
            return candidate
    return None


def parse_brief(path: Path) -> dict:
    if not path.exists():
        return {}
    text = read(path)
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.M)
    depth_match = re.search(r"深度[：:]\s*(L[0-4])", text)
    status_match = re.search(r"状态[：:]\s*([^\s·|]+)", text)
    return {
        "title": title_match.group(1).strip() if title_match else path.parent.name,
        "depth": depth_match.group(1) if depth_match else "",
        "status": status_match.group(1) if status_match else "",
    }


def latest_report(topic: Path) -> Path | None:
    reports = sorted(topic.glob("report-v*.md"), key=lambda p: p.stat().st_mtime)
    return reports[-1] if reports else None


def latest_mtime(topic: Path) -> str:
    times = [p.stat().st_mtime for p in topic.glob("*") if p.is_file()]
    if not times:
        return ""
    return date.fromtimestamp(max(times)).isoformat()


def count_evidence(rows: list[dict]) -> dict:
    counts = {"total": 0, "A": 0, "B": 0, "C": 0, "verified": 0, "pending": 0, "conflict": 0}
    for row in rows:
        status = row.get("status", "")
        grade = row.get("grade", "").upper()
        url = row.get("url", "")
        if "作废" in status:
            continue
        counts["total"] += 1
        if grade.startswith("A"):
            counts["A"] += 1
        elif grade.startswith("B"):
            counts["B"] += 1
        elif grade.startswith("C"):
            counts["C"] += 1
        if "已核" in status and url.startswith("http"):
            counts["verified"] += 1
        if "待核" in status:
            counts["pending"] += 1
        if "冲突" in status:
            counts["conflict"] += 1
    return counts


def parse_index_rows(text: str) -> dict:
    block = text
    if AUTO_BEGIN in text and AUTO_END in text:
        block = text.split(AUTO_BEGIN, 1)[1].split(AUTO_END, 1)[0]
    rows = {}
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = split_cells(line)
        if len(cells) < 7 or cells[0] in ("题号", "") or set(cells[0]) <= {"-", ":"}:
            continue
        rows[cells[0]] = cells
    return rows


def render_index_rows() -> str:
    existing = {}
    if INDEX_PATH.exists():
        existing = parse_index_rows(read(INDEX_PATH))
    lines = [
        "| 题号 | 题目 | 深度 | 状态 | 下一步 | 最后更新 | 入口 |",
        "|---|---|---|---|---|---|---|",
    ]
    for topic in topic_dirs():
        brief = parse_brief(topic / "brief.md")
        rows = parse_evidence(read(topic / "evidence.md")) if (topic / "evidence.md").exists() else []
        counts = count_evidence(rows)
        old = existing.get(topic.name)
        status = brief.get("status") or (old[3] if old and old[3] else "研究中")
        next_step = old[4] if old and old[4] else "待填"
        depth = brief.get("depth") or (old[2] if old else "L1")
        updated = latest_mtime(topic) or date.today().isoformat()
        lines.append(
            f"| {topic.name} | {brief.get('title', topic.name)} | {depth} | {status} | "
            f"{next_step} | {updated} | `topics/{topic.name}/` |"
        )
    return "\n".join(lines)


def update_index(extra_note: str | None = None) -> None:
    if not INDEX_PATH.exists():
        return
    text = read(INDEX_PATH)
    block = render_index_rows()
    if AUTO_BEGIN in text and AUTO_END in text:
        head, rest = text.split(AUTO_BEGIN, 1)
        _, tail = rest.split(AUTO_END, 1)
        text = head + AUTO_BEGIN + "\n" + block + "\n" + AUTO_END + tail
    else:
        text = text.rstrip() + "\n\n" + AUTO_BEGIN + "\n" + block + "\n" + AUTO_END + "\n"
    write(INDEX_PATH, text)


def today_iso() -> str:
    return date.today().isoformat()
