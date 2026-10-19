#!/usr/bin/env python3
"""把课题报告 Markdown 渲染成自包含 HTML 一页报告（手机可读、可打印 PDF）。"""
from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

import research_common as rc

CSS = """
:root{
  --bg:#f4f7fb; --paper:#ffffff; --ink:#1e2a36; --muted:#5b6b7c;
  --line:#dfe8f1; --blue:#3f7fa8; --blue-soft:#eaf3f9;
  --orange:#d98343; --orange-soft:#fdf3e9;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:16px;line-height:1.75}
.page{max-width:820px;margin:0 auto;padding:36px 22px 72px}
.kicker{font-size:12px;letter-spacing:.12em;color:var(--blue);text-transform:uppercase;font-weight:600}
h1{font-size:30px;line-height:1.3;margin:10px 0;letter-spacing:-.01em}
.meta{color:var(--muted);font-size:13px;margin:0 0 22px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.card{background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--blue);
  border-radius:10px;padding:18px 20px;margin:0 0 26px;box-shadow:0 6px 18px rgba(31,58,82,.05)}
.card .row{display:grid;grid-template-columns:76px 1fr;gap:10px;padding:8px 0;border-bottom:1px dashed var(--line)}
.card .row:last-child{border-bottom:0}
.card .label{color:var(--blue);font-weight:600;font-size:14px}
.card .value{font-size:15px}
.card .row:first-child .value{font-size:17px;font-weight:600}
nav.toc{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:0 0 30px;font-size:14px}
nav.toc .toc-title{font-weight:600;color:var(--muted);font-size:12px;letter-spacing:.08em;margin-bottom:6px}
nav.toc a{color:var(--ink);text-decoration:none;display:block;padding:3px 0;border:0}
nav.toc a.lv3{padding-left:16px;color:var(--muted);font-size:13px}
h2{font-size:22px;margin:38px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--blue-soft);line-height:1.4}
h3{font-size:18px;margin:26px 0 10px;color:#2c3e50}
p{margin:0 0 14px}
strong{font-weight:600}
a{color:var(--blue);text-decoration:none;border-bottom:1px solid rgba(63,127,168,.35)}
.cite{display:inline-block;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  font-size:11px;line-height:1.6;color:#2c6a92;background:var(--blue-soft);border-radius:4px;
  padding:0 4px;margin:0 1px;vertical-align:1px}
.table-wrap{overflow-x:auto;margin:16px 0 20px;border:1px solid var(--line);border-radius:8px;background:var(--paper)}
table{border-collapse:collapse;width:100%;min-width:460px;font-size:14px}
th{background:var(--blue-soft);color:#26485f;text-align:left;font-weight:600;padding:8px 10px;
  border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th,td{overflow-wrap:anywhere}
tr:last-child td{border-bottom:0}
tbody tr:nth-child(even){background:#fafcfe}
blockquote{margin:16px 0;padding:10px 16px;background:var(--orange-soft);
  border-left:3px solid var(--orange);color:#6b4a2f;border-radius:0 8px 8px 0;font-size:14px}
blockquote p{margin:0}
ul,ol{padding-left:22px;margin:0 0 14px}
li{margin:4px 0}
hr{border:0;border-top:1px solid var(--line);margin:26px 0}
code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.9em;
  background:#eef3f8;border-radius:4px;padding:1px 4px}
pre{background:#f1f5f9;border:1px solid var(--line);border-radius:8px;padding:12px;overflow-x:auto}
pre code{background:none;padding:0}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);
  font-size:12px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
@media(max-width:640px){
  .page{padding:22px 14px 56px}
  h1{font-size:24px}
  h2{font-size:19px}
  h3{font-size:16px}
  .card{padding:14px 15px}
  .card .row{grid-template-columns:64px 1fr;gap:8px}
  .card .label{font-size:13px}
  table{min-width:0;font-size:13px}
  th,td{padding:6px 8px}
}
@media print{
  body{background:#fff}
  .page{max-width:none;padding:0}
  .card,nav.toc{box-shadow:none}
  nav.toc{display:none}
  h2{page-break-after:avoid}
  table{min-width:0}
  tr,img{page-break-inside:avoid}
  a{color:inherit;border:0}
  .cite{background:none;border:1px solid #ccc}
}
"""


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        out,
    )
    out = re.sub(r"\[(E\d{2,})\]", r'<span class="cite">\1</span>', out)
    return out


def is_block_start(line: str) -> bool:
    s = line.strip()
    return (
        not s
        or s.startswith("#")
        or s.startswith("|")
        or s.startswith(">")
        or s.startswith("```")
        or s in ("---", "***", "___")
        or re.match(r"^([-*]|\d+\.)\s+", s) is not None
    )


class Renderer:
    def __init__(self):
        self.toc = []
        self.counter = 0

    def heading(self, level: int, text: str) -> str:
        self.counter += 1
        anchor = f"sec-{self.counter}"
        if level in (2, 3):
            self.toc.append((level, text, anchor))
        return f'<h{level} id="{anchor}">{inline(text)}</h{level}>'

    def render(self, lines: list[str]) -> str:
        out = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped:
                i += 1
                continue

            if stripped.startswith("```"):
                lang = stripped[3:].strip()
                i += 1
                code = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code.append(lines[i])
                    i += 1
                i += 1
                cls = f' class="language-{html.escape(lang)}"' if lang else ""
                out.append(f"<pre><code{cls}>{html.escape(chr(10).join(code))}</code></pre>")
                continue

            m = re.match(r"^(#{1,4})\s+(.+)$", stripped)
            if m:
                out.append(self.heading(len(m.group(1)), m.group(2).strip()))
                i += 1
                continue

            if stripped in ("---", "***", "___"):
                out.append("<hr>")
                i += 1
                continue

            if stripped.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                out.append(self.table(table_lines))
                continue

            if stripped.startswith(">"):
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(lines[i].strip()[1:].strip())
                    i += 1
                out.append("<blockquote><p>" + "<br>".join(inline(q) for q in quote if q) + "</p></blockquote>")
                continue

            if re.match(r"^[-*]\s+", stripped):
                items = []
                while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                    items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                    i += 1
                out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
                continue

            if re.match(r"^\d+\.\s+", stripped):
                items = []
                while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                    items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                    i += 1
                out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
                continue

            para = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
        return "\n".join(out)

    @staticmethod
    def table(lines: list[str]) -> str:
        if len(lines) < 2:
            return ""
        header = rc.split_cells(lines[0])
        body = []
        for line in lines[2:]:
            cells = rc.split_cells(line)
            if not cells or set("".join(cells)) <= {"-", ":"}:
                continue
            body.append(cells)
        head_html = "".join(f"<th>{inline(cell)}</th>" for cell in header)
        rows = []
        for cells in body:
            padded = cells + [""] * (len(header) - len(cells))
            rows.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in padded[: len(header)]) + "</tr>")
        return (
            '<div class="table-wrap"><table><thead><tr>'
            + head_html
            + "</tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )


CARD_FIELDS = ("结论", "关键数字", "动作", "反证", "置信度")


def extract_card(lines: list[str]) -> tuple[str, list[str]]:
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^##\s+结论卡\s*$", line.strip()):
            start = i
            break
    if start is None:
        return "", lines
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^#{1,2}\s+", lines[j].strip()):
            end = j
            break
    section = lines[start + 1:end]
    rows = []
    for line in section:
        m = re.match(r"^\s*[-*]\s*(?:\*\*)?(" + "|".join(CARD_FIELDS) + r")(?:\*\*)?\s*[：:]\s*(.+)$", line)
        if m:
            rows.append((m.group(1), m.group(2).strip()))
    if not rows:
        return "", lines
    card_html = ['<div class="card" id="conclusion">']
    for label, value in rows:
        card_html.append(
            f'<div class="row"><div class="label">{html.escape(label)}</div>'
            f'<div class="value">{inline(value)}</div></div>'
        )
    card_html.append("</div>")
    remaining = lines[:start] + lines[end:]
    return "\n".join(card_html), remaining


def extract_title_meta(lines: list[str]) -> tuple[str, str, list[str]]:
    title = "研究报告"
    meta = ""
    rest = list(lines)
    for i, line in enumerate(rest):
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            title = m.group(1).strip()
            rest = rest[:i] + rest[i + 1:]
            break
    for i, line in enumerate(rest):
        if not line.strip():
            continue
        if line.strip().startswith(">"):
            values = []
            j = i
            while j < len(rest) and rest[j].strip().startswith(">"):
                values.append(rest[j].strip()[1:].strip())
                j += 1
            meta = " · ".join(v for v in values if v)
            rest = rest[:i] + rest[j:]
        break
    return title, meta, rest


def build_html(md_path: Path, title_override: str | None = None) -> str:
    text = rc.read(md_path)
    lines = text.splitlines()
    title, meta, rest = extract_title_meta(lines)
    card_html, rest = extract_card(rest)
    renderer = Renderer()
    body = renderer.render(rest)

    toc_items = []
    if card_html:
        toc_items.append((2, "结论卡", "conclusion"))
    toc_items.extend(renderer.toc)
    toc = []
    for level, label, anchor in toc_items:
        cls = "lv3" if level == 3 else ""
        toc.append(f'<a class="{cls}" href="#{anchor}">{inline(label)}</a>')
    card = rc.infer_card(md_path)
    show_toc = bool(card) and card.get("key") in ("L2", "L3", "L4") and len(toc_items) > 3
    toc_html = (
        '<nav class="toc"><div class="toc-title">本页内容</div>' + "".join(toc) + "</nav>"
        if show_toc else ""
    )

    kicker = "研究助理"
    if card:
        kicker += f" · {card.get('key', '')} {card.get('name', '')}"
    final_title = title_override or title
    today = date.today().isoformat()
    meta_html = f'<p class="meta">{inline(meta)}</p>' if meta else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(final_title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
<header>
<div class="kicker">{html.escape(kicker)}</div>
<h1>{html.escape(final_title)}</h1>
{meta_html}
{card_html}
</header>
{toc_html}
<main>
{body}
</main>
<footer>
<span>ResearchAssociate · 研究助理</span>
<span>{today}</span>
</footer>
</div>
</body>
</html>
"""


def main(argv=None) -> int:
    rc.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", help="报告 Markdown 路径")
    ap.add_argument("-o", "--output", help="输出 HTML 路径；默认同目录同名 .html")
    ap.add_argument("--title", help="覆盖页面标题")
    args = ap.parse_args(argv)

    report = Path(args.report)
    if not report.exists():
        print(f"错误：报告不存在：{report}", file=sys.stderr)
        return 2
    output = Path(args.output) if args.output else report.with_suffix(".html")
    try:
        content = build_html(report, args.title)
    except OSError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    rc.write(output, content)
    print(f"已生成：{output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
