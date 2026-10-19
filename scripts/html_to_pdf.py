# -*- coding: utf-8 -*-
"""用 Chrome/Edge headless 把 HTML 打印为 PDF。

用法:
    python html_to_pdf.py <input.html> <output.pdf> [--browser <chrome|edge|auto>]
"""
import argparse
import subprocess
import sys
from pathlib import Path

BROWSER_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "edge": [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ],
}

def find_browser(which):
    keys = ["chrome", "edge"] if which == "auto" else [which]
    for k in keys:
        for p in BROWSER_PATHS[k]:
            if Path(p).exists():
                return Path(p)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=str)
    ap.add_argument("output", type=str)
    ap.add_argument("--browser", type=str, default="auto")
    args = ap.parse_args()

    html_path = Path(args.input).resolve()
    out_path = Path(args.output).resolve()
    if not html_path.exists():
        sys.stderr.write(f"HTML 不存在: {html_path}\n")
        sys.exit(2)

    browser = find_browser(args.browser)
    if browser is None:
        sys.stderr.write("未找到 Chrome/Edge，请安装后重试。\n")
        sys.exit(3)

    url = "file:///" + str(html_path).replace("\\", "/")
    cmd = [
        str(browser), "--headless", "--disable-gpu",
        "--no-pdf-header-footer", "--print-to-pdf=" + str(out_path), url,
    ]
    subprocess.run(cmd, check=False, capture_output=True, timeout=180)
    if out_path.exists() and out_path.stat().st_size > 0:
        print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
    else:
        sys.stderr.write("PDF 生成失败。\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
