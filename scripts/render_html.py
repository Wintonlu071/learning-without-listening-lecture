# -*- coding: utf-8 -*-
"""把 Markdown 源稿渲染为带样式的独立 HTML（含 MathJax）。

用法:
    python render_html.py <input.md> <output.html> [--title TITLE] [--tag TAG] [--subtitle SUBTITLE]

不提供 title/tag/subtitle 时自动取 md 的第一个 H1 作标题。
"""
import argparse
import html
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "template.html"

def inline(text: str) -> str:
    """处理行内标记；$...$ 与 $$...$$ 原样保留给 MathJax。"""
    text = html.escape(text, quote=False)
    # 先保护数学，避免被加粗/斜体破坏
    math = []
    def stash(m):
        math.append(m.group(0))
        return f"\u0000{len(math)-1}\u0000"
    text = re.sub(r"\$\$[^$]+\$\$|\$[^$]+\$", stash, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    for i, m in enumerate(math):
        text = text.replace(f"\u0000{i}\u0000", m)
    return text

def block_to_html(lines, start):
    """从 start 行开始，把一段 block 转成 HTML，返回 (html, 下一行索引)。"""
    first = lines[start]
    # 围栏代码块
    if first.strip().startswith("```"):
        buf = [first]
        i = start + 1
        while i < len(lines) and not lines[i].strip().startswith("```"):
            buf.append(lines[i])
            i += 1
        if i < len(lines):
            buf.append(lines[i])
            i += 1
        code = "\n".join(buf[1:-1])
        lang = buf[0].strip()[3:].strip()
        return f'<pre><code class="language-{html.escape(lang)}">{html.escape(code)}</code></pre>\n', i
    # 表格
    if "|" in first and start + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|[\s:|-]*$", lines[start+1]):
        header = [c.strip() for c in first.strip().strip("|").split("|")]
        i = start + 2
        rows = []
        while i < len(lines) and "|" in lines[i] and lines[i].strip():
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        h = "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>\n"
        b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>\n" for r in rows)
        return f"<table>\n{h}{b}</table>\n", i
    # 标题
    m = re.match(r"^(#{1,6})\s+(.*)$", first)
    if m:
        lvl = len(m.group(1))
        return f"<h{lvl}>{inline(m.group(2))}</h{lvl}>\n", start + 1
    # 引用块
    if first.strip().startswith(">"):
        buf = []
        i = start
        while i < len(lines) and lines[i].strip().startswith(">"):
            buf.append(lines[i].strip()[1:].strip())
            i += 1
        return f'<blockquote class="box">{"<br>".join(inline(x) for x in buf)}</blockquote>\n', i
    # 无序列表
    if re.match(r"^\s*[-*+]\s+", first):
        buf = []
        i = start
        while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
            buf.append(inline(re.sub(r"^\s*[-*+]\s+", "", lines[i])))
            i += 1
        return "<ul>" + "".join(f"<li>{x}</li>" for x in buf) + "</ul>\n", i
    # 有序列表
    if re.match(r"^\s*\d+\.\s+", first):
        buf = []
        i = start
        while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
            buf.append(inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
            i += 1
        return "<ol>" + "".join(f"<li>{x}</li>" for x in buf) + "</ol>\n", i
    # 分隔线
    if first.strip() in ("---", "***", "___"):
        return "<hr/>\n", start + 1
    # 普通段落（合并到空行）
    buf = [first]
    i = start + 1
    while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|\||>|[-*+]\s|\d+\.\s|---|\*\*\*|___)", lines[i]):
        buf.append(lines[i])
        i += 1
    return f"<p>{inline(' '.join(x.strip() for x in buf))}</p>\n", i

def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        frag, i = block_to_html(lines, i)
        out.append(frag)
    return "".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=str)
    ap.add_argument("output", type=str)
    ap.add_argument("--title", type=str, default=None)
    ap.add_argument("--tag", type=str, default="REVIEW")
    ap.add_argument("--subtitle", type=str, default="")
    args = ap.parse_args()

    md = Path(args.input).read_text(encoding="utf-8")
    body = markdown_to_html(md)

    title = args.title
    if not title:
        m = re.search(r"^#\s+(.+)$", md, flags=re.M)
        title = m.group(1).strip() if m else Path(args.input).stem

    tpl = TEMPLATE.read_text(encoding="utf-8")
    tpl = tpl.replace("__TITLE__", html.escape(title))
    tpl = tpl.replace("__TAG__", html.escape(args.tag))
    tpl = tpl.replace("__SUBTITLE__", html.escape(args.subtitle))
    tpl = tpl.replace("__BODY__", body)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
