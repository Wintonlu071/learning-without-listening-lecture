# -*- coding: utf-8 -*-
"""提交前扫描目录中的疑似密钥/令牌/私钥，命中则退出码非 0。

用法:
    python check_no_secrets.py [目录]      # 默认扫描技能根目录
"""
import re
import sys
from pathlib import Path

PATTERNS = [
    (r"sk-[A-Za-z0-9]{16,}", "OpenAI 风格密钥"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub PAT"),
    (r"github_pat_[A-Za-z0-9_]{20,}", "GitHub fine-grained PAT"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}", "API key 赋值"),
    (r"(?i)token\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{12,}", "token 赋值"),
    (r"(?i)secret\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}", "secret 赋值"),
    (r"(?i)bearer\s+[A-Za-z0-9\-\._~]{20,}", "Bearer 令牌"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私钥"),
]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
SKIP_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".m4a", ".mp3", ".wav", ".pdf", ".exe", ".dll", ".so"}

def scan(root: Path):
    hits = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in SKIP_EXTS:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat, label in PATTERNS:
            for m in re.finditer(pat, text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append((p, line, label, m.group(0)[:40]))
    return hits

def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    hits = scan(root)
    if hits:
        for p, line, label, snippet in hits:
            print(f"[命中] {label}: {p}:{line}  ->  {snippet!r}")
        print(f"\n共 {len(hits)} 处疑似密钥，请处理后再提交。")
        sys.exit(1)
    print("OK: 未发现疑似密钥/令牌/私钥。")
    sys.exit(0)

if __name__ == "__main__":
    main()
