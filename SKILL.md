---
name: tech-post
description: Create tech blog posts as paginated images for social media (小红书/REDNote). Converts Markdown to styled HTML via WeasyPrint, then to 4K 3:4 PNG pages via PyMuPDF. Use when asked to create a tech post, blog post images, 小红书图文, or convert markdown to styled image pages.
---

# Tech Post

Convert Markdown tech posts into paginated 3:4 images for social media.

## Pipeline

1. **Write/translate** — Draft or translate content in Markdown
2. **Render** — `scripts/md2img.py` converts MD → HTML → PDF → PNG pages

## Usage

```bash
/opt/homebrew/bin/python3.12 SKILL_DIR/scripts/md2img.py <input.md> [output_dir]
```

- Output: `{stem}_p1.png`, `{stem}_p2.png`, ... + `{stem}.pdf`
- Default output dir: same as input file

## Features

- 3:4 aspect ratio (108mm × 144mm), 4K resolution (1016 DPI)
- Noto Serif CJK SC font (serif), warm beige background (#FDF8F0)
- Color-coded headings: h1 deep brown, h2 burnt orange, h3 light brown
- Pygments syntax highlighting with language labels on code blocks
- Code blocks: 9px mono, word-wrap, `break-inside: avoid` (no mid-page splits)
- TL;DR block injected after first h1
- Monospace fallback includes CJK fonts for Chinese comments

## Customization

Edit CSS variables in `scripts/md2img.py`:
- `BG_COLOR` — page background (default `#FDF8F0`)
- `DPI` — output resolution (default 1016 for 4K)
- `PAGE_W_MM` / `PAGE_H_MM` — page dimensions (default 108×144, 3:4)
- h1/h2/h3 colors in CSS `h1 {}`, `h2 {}`, `h3 {}` blocks

## TL;DR

Auto-extracted from the `## TL;DR` section in the markdown. No need to hardcode — just include a `## TL;DR` heading in your post and the script will extract the text, apply 盘古之白 spacing, and render it as the cover block after the title.

## 盘古之白 (CJK-Latin Spacing)

The script automatically adds spaces between CJK and Latin/digit characters (盘古之白) in both the TL;DR block and the body text. Code blocks are excluded. No manual spacing needed in the markdown source.

## Dependencies

```bash
/opt/homebrew/bin/python3.12 -m pip install --break-system-packages weasyprint pymupdf markdown Pygments
brew install pango glib font-noto-serif-cjk-sc font-noto-sans-cjk-sc
```

## Workflow Tips

- Keep code blocks in English to avoid CJK font rendering issues in monospace
- For Chinese posts: draft in English first, translate via sub-agent (Sonnet recommended for technical tone)
- Target ≤2000 Chinese characters (excluding code) for 小红书
- Send images via `message` tool with `filePath` from output dir
