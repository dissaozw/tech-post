# tech-post

Convert Markdown tech posts into paginated 4K images for social media (小红书/REDNote).

![3:4 ratio](https://img.shields.io/badge/ratio-3%3A4-blue) ![4K](https://img.shields.io/badge/resolution-4K-green) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-yellow)

## What it does

`md2img.py` takes a Markdown file and produces a series of beautifully typeset PNG pages ready to post on REDNote (小红书), Instagram, or any platform that favors image carousels.

**Pipeline:** Markdown → HTML (with Pygments syntax highlighting) → PDF (WeasyPrint) → PNG pages (PyMuPDF)

## Features

- **3:4 aspect ratio** — optimized for mobile feeds
- **4K resolution** (4320 × 5760) — crisp on any screen
- **CJK support** — Noto Serif CJK SC + Noto Sans CJK SC
- **Syntax highlighting** — Pygments with language labels
- **Code blocks don't split across pages** — `break-inside: avoid`
- **Warm beige theme** — easy on the eyes
- **Color-coded headings** — h1 deep brown, h2 burnt orange, h3 light brown
- **TL;DR block** — auto-injected after the title

## Quick Start

### Install dependencies

```bash
# Python packages
pip install weasyprint pymupdf markdown Pygments

# System dependencies (macOS)
brew install pango glib
brew install --cask font-noto-serif-cjk-sc font-noto-sans-cjk-sc
```

### Run

```bash
python scripts/md2img.py my-post.md output/
```

Output: `output/my-post_p1.png`, `output/my-post_p2.png`, ... + `output/my-post.pdf`

## Customization

Edit the CSS in `scripts/md2img.py`:

| Variable | Default | Description |
|---|---|---|
| `BG_COLOR` | `#FDF8F0` | Page background (warm beige) |
| `DPI` | `1016` | Output resolution (4K) |
| `PAGE_W_MM × PAGE_H_MM` | `108 × 144` | Page dimensions (3:4) |
| h1 color | `#8B4513` | Deep brown |
| h2 color | `#B8602A` | Burnt orange |
| h3 color | `#C98A5E` | Light brown |

## OpenClaw Skill

This repo is also an [OpenClaw](https://github.com/openclaw/openclaw) skill. Clone it into your skills directory:

```bash
cd ~/.openclaw/skills
git clone https://github.com/zhiyuanw0/tech-post.git
```

Then ask your agent: "帮我把这篇文章转成小红书图文"

## Example

Input: A Chinese tech blog post about AI memory systems

Output: 13 paginated 4K images with syntax-highlighted code blocks, warm beige background, and serif typography.

## License

MIT
