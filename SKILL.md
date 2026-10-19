---
name: learning-without-listening-teacher
description: 根据课堂PPT与课堂录音纪要（AI纪要docx）自动生成课程复习资料（Review Guide）与结构化知识体系（Knowledge System）。当用户要求"整理复习笔记/知识点/知识体系/quiz复习资料/根据PPT和录音纪要生成复习文件"时使用。输出语言按PPT主导语言决定：英文PPT为主则英文为主+陌生术语加中文注释，中文PPT为主则中文输出。不含任何API密钥，不自动转录音频。
---

# Learning Without Listening Teacher

把一门课的「课堂 PPT + 课堂录音纪要」自动整理成两份可直接复习的材料：
1. **复习资料 Review Guide** —— 考前背诵与刷题用。
2. **结构化知识体系 Knowledge System** —— 建立整门课的主线与依赖图。

## 何时使用

- 用户要求根据课堂 PPT、课堂录音纪要、作业整理复习资料、复习笔记、知识体系、Quiz 复习资料。
- 课程目录通常形如：`ppt/` 或根目录下的课件 PDF、`<章节>/` 下的 `*AI纪要*.docx`、`homework/` 下的作业 PDF。

## 工作流程（严格按顺序）

1. **盘点输入**：列出课程目录下所有课件 PDF、`*AI纪要*.docx`、作业 PDF、音频文件，并向用户简要汇报找到什么。
   - 有 `*AI纪要*.docx` → 作为课堂纪要来源，优先参考。
   - 没有纪要、只有音频（`.m4a/.mp3/.wav`）→ 停下询问用户是否启用转录音频功能；本技能不内置转录服务、不内置任何密钥。
   - 没有任何录音相关文件 → 只用 PPT + 作业等已有课件。

2. **抽取与语言判定**：
   ```bash
   python scripts/extract_sources.py "<课程目录>" --out "<课程目录>/review"
   ```
   生成 `course_sources.md`（全部文本素材，含盘点清单）和 `language.txt`（`en` 或 `zh`，基于 PPT 中文字符占比）。

3. **语言规则**（详见 `references/language-rule.md`）：
   - `en`：正文、定义、讲解用英文；对可能不认识的术语或难句加中文注释（如 `outlier（异常值）`），并附中英术语表。
   - `zh`：全文中文，术语保留英文原文。

4. **生成两份材料**（结构要求见 `references/review-guide.md` 与 `references/knowledge-system.md`）：
   - 先写 Markdown 源稿，用 `scripts/render_html.py` 渲染为带样式 HTML，再用 `scripts/html_to_pdf.py` 转 PDF。
   - 文件名含课程名与范围，例如 `Calculus_Quiz1_Review_Guide.md`、`Calculus_Knowledge_System.md`。
   - 公式用 LaTeX：行内 `$...$`，块级 `$$...$$`；渲染时由 MathJax 显示。

5. **输出位置**：默认写入 `<课程目录>/review/`，三份格式同名并列（`.md` / `.html` / `.pdf`）。

## 安全红线（必须遵守）

- 本技能与脚本**不含任何 API 密钥**；不得读取、复制或提交 `~/.codex/auth.json`、`config.toml` 等凭证文件。
- 不把 PPT、音频、纪要原件提交到公开仓库；GitHub 仓库只含本技能自身。
- 提交/推送前运行 `python scripts/check_no_secrets.py`，并执行 `git grep -nEi 'sk-|api[_-]?key|token|secret|bearer'`，命中则中止。

## 关键文件

- `references/language-rule.md` —— 语言判定与双语输出规范
- `references/review-guide.md` —— 复习资料结构与质量要求
- `references/knowledge-system.md` —— 知识体系结构与质量要求
- `scripts/extract_sources.py` —— 扫描与文本抽取、语言判定
- `scripts/render_html.py` —— Markdown → 样式化 HTML
- `scripts/html_to_pdf.py` —— HTML → PDF（Chrome headless）
- `scripts/check_no_secrets.py` —— 提交前密钥扫描
