#!/usr/bin/env python3
"""Convert Markdown to paginated 3:4 images via WeasyPrint (HTML→PDF) + PyMuPDF (PDF→PNG)."""

import re
import sys
from pathlib import Path
import markdown
import weasyprint
import fitz  # PyMuPDF

# --- Config ---
PAGE_W_MM = 108  # 3:4 ratio at ~1080px (10px/mm)
PAGE_H_MM = 144
DPI = 1016  # renders ~4320px wide (4K)

CSS = """
@page {
    size: 108mm 144mm;
    margin: 8mm 6mm 10mm 6mm;
}

body {
    font-family: "Noto Serif CJK SC", "Noto Sans CJK SC", "PingFang SC", serif;
    font-size: 14px;
    line-height: 1.8;
    color: #1a1a1a;
    background: #FDF8F0;
}

h1 {
    font-size: 22px;
    font-weight: 700;
    color: #8B4513;
    border-left: 4px solid #8B4513;
    padding-left: 12px;
    margin-top: 18px;
    margin-bottom: 10px;
    line-height: 1.4;
}

h2 {
    font-size: 18px;
    font-weight: 700;
    color: #B8602A;
    margin-top: 16px;
    margin-bottom: 8px;
    line-height: 1.4;
}

h3 {
    font-size: 16px;
    font-weight: 700;
    color: #C98A5E;
    margin-top: 14px;
    margin-bottom: 6px;
    border-left: 3px solid #C98A5E;
    padding-left: 8px;
}

p {
    margin: 6px 0;
    text-align: justify;
}

ul, ol {
    padding-left: 20px;
    margin: 6px 0;
}

li {
    margin: 3px 0;
}

code {
    font-family: "SF Mono", "Menlo", "Monaco", "PingFang SC", "STHeiti", monospace;
    font-size: 12px;
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 3px;
    color: #c7254e;
}

pre {
    background: #f5f5f5;
    border-radius: 6px;
    padding: 10px 12px;
    margin: 8px 0;
    overflow: hidden;
    line-height: 1.4;
    word-wrap: break-word;
    white-space: pre-wrap;
    position: relative;
    break-inside: avoid;
    page-break-inside: avoid;
}

pre code {
    font-family: "SF Mono", "Menlo", "PingFang SC", "STHeiti", monospace;
    font-size: 9px;
    background: none;
    padding: 0;
    color: #333;
    word-wrap: break-word;
    white-space: pre-wrap;
}

/* Pygments syntax highlighting (friendly theme) */
.codehilite { background: #f5f5f5; border-radius: 6px; padding: 10px 12px; margin: 8px 0; overflow: hidden; position: relative; break-inside: avoid; page-break-inside: avoid; }
.codehilite pre { background: none; padding: 0; margin: 0; border-radius: 0; }
.codehilite code { font-size: 9px; font-family: "SF Mono", "Menlo", "PingFang SC", "STHeiti", monospace; }
.codehilite .hll { background-color: #ffffcc }
.codehilite .c { color: #999988; font-style: italic } /* Comment */
.codehilite .k { color: #d73a49; font-weight: bold } /* Keyword */
.codehilite .o { color: #666666 } /* Operator */
.codehilite .cm { color: #999988; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #999999; font-weight: bold } /* Comment.Preproc */
.codehilite .c1 { color: #999988; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #999999; font-weight: bold; font-style: italic }
.codehilite .gd { color: #a31515 } /* Generic.Deleted */
.codehilite .gi { color: #22863a } /* Generic.Inserted */
.codehilite .kc { color: #d73a49; font-weight: bold }
.codehilite .kd { color: #d73a49; font-weight: bold }
.codehilite .kn { color: #d73a49; font-weight: bold }
.codehilite .kp { color: #d73a49 }
.codehilite .kr { color: #d73a49; font-weight: bold }
.codehilite .kt { color: #445588; font-weight: bold }
.codehilite .m { color: #005cc5 } /* Number */
.codehilite .s { color: #032f62 } /* String */
.codehilite .na { color: #008080 } /* Name.Attribute */
.codehilite .nb { color: #0086b3 } /* Name.Builtin */
.codehilite .nc { color: #445588; font-weight: bold } /* Name.Class */
.codehilite .no { color: #008080 }
.codehilite .ni { color: #800080 }
.codehilite .ne { color: #990000; font-weight: bold }
.codehilite .nf { color: #6f42c1; font-weight: bold } /* Name.Function */
.codehilite .nn { color: #555555 } /* Name.Namespace */
.codehilite .nt { color: #22863a } /* Name.Tag */
.codehilite .nv { color: #008080 } /* Name.Variable */
.codehilite .ow { font-weight: bold }
.codehilite .w { color: #bbbbbb }
.codehilite .mi { color: #005cc5 }
.codehilite .mf { color: #005cc5 }
.codehilite .mh { color: #005cc5 }
.codehilite .mo { color: #005cc5 }
.codehilite .sb { color: #032f62 }
.codehilite .sc { color: #032f62 }
.codehilite .sd { color: #032f62 }
.codehilite .s2 { color: #032f62 }
.codehilite .se { color: #032f62 }
.codehilite .sh { color: #032f62 }
.codehilite .si { color: #032f62 }
.codehilite .sx { color: #032f62 }
.codehilite .sr { color: #032f62 }
.codehilite .s1 { color: #032f62 }
.codehilite .ss { color: #005cc5 }
.codehilite .bp { color: #999999 }
.codehilite .vc { color: #008080 }
.codehilite .vg { color: #008080 }
.codehilite .vi { color: #008080 }
.codehilite .il { color: #005cc5 }

/* TOC page */
.toc-page {
    page-break-after: always;
    padding-top: 8mm;
}
.toc-title {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    color: #8B4513;
    border-left: none;
    padding-left: 0;
    margin-bottom: 12px;
    letter-spacing: 8px;
}
.toc-list {
    margin-top: 8px;
}
.toc-h1 {
    font-size: 11px;
    font-weight: 700;
    color: #8B4513;
    padding: 3px 0;
    border-bottom: 1px solid #E8DDD0;
}
.toc-h2 {
    font-size: 10px;
    font-weight: 600;
    color: #B8602A;
    padding: 2px 0;
}
.toc-h3 {
    font-size: 9px;
    font-weight: 400;
    color: #C98A5E;
    padding: 2px 0;
}

/* Cover page */
.cover-page {
    page-break-after: always;
    padding-top: 25mm;
    text-align: center;
}
.cover-title {
    font-size: 26px;
    font-weight: 700;
    color: #8B4513;
    border-left: none;
    padding-left: 0;
    margin-bottom: 20px;
    line-height: 1.5;
    text-align: center;
}
.cover-tldr {
    text-align: left;
    margin: 20px 4mm 0 4mm;
    padding: 12px 14px;
    background: rgba(139, 69, 19, 0.06);
    border-radius: 6px;
    border-left: 3px solid #8B4513;
}
.cover-tldr-title {
    font-size: 13px;
    font-weight: 700;
    color: #8B4513;
    margin-bottom: 6px;
}
.cover-tldr p {
    font-size: 11px;
    line-height: 1.7;
    color: #444;
    margin: 3px 0;
}

/* Language label */
.code-lang-label {
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 8px;
    color: #999;
    background: #eaeaea;
    padding: 1px 6px;
    border-radius: 3px;
    margin-bottom: 4px;
    display: inline-block;
}

strong {
    font-weight: 700;
    color: #111;
}

em {
    font-style: italic;
    color: #555;
}

hr {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 12px 0;
}

blockquote {
    border-left: 3px solid #ddd;
    padding-left: 10px;
    color: #666;
    margin: 8px 0;
}
"""


def md_to_html(md_text):
    """Convert markdown to HTML with fenced code blocks."""
    # Remove front-matter-like lines (draft notes)
    lines = md_text.split("\n")
    filtered = []
    for line in lines:
        if line.strip().startswith("*Draft") or line.strip().startswith("*草稿") or line.strip().startswith("*Running"):
            continue
        filtered.append(line)
    md_text = "\n".join(filtered)

    # Insert TLDR after the first h1 heading
    import re as _re2
    tldr_block = '''
<div class="cover-tldr">
<div class="cover-tldr-title">TL;DR</div>
<p>OpenClaw的记忆系统基于纯Markdown文件，分为每日笔记和长期记忆两层架构。智能体每次会话加载上下文文件，通过压缩前刷新机制保证记忆不丢失。搜索层可选内置向量搜索或本地QMD。核心思路：文件即真相，确定性注入优于概率检索。</p>
</div>
'''
    cover_html = ''
    toc_html = ''

    # Add language labels before code blocks
    import re as _re
    def _add_lang_label(m):
        lang = m.group(1) or ""
        label = f'<div class="code-lang-label">{lang}</div>\n' if lang else ""
        return f'{label}```{lang}'
    md_text = _re.sub(r'^```(\w*)', _add_lang_label, md_text, flags=_re.MULTILINE)

    html_body = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "nl2br", "codehilite"],
        extension_configs={
            "codehilite": {
                "guess_lang": False,
                "css_class": "codehilite",
            }
        },
    )

    # Insert TLDR after first h1 in rendered HTML
    html_body = html_body.replace('</h1>', '</h1>' + tldr_block, 1)

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""


def html_to_pdf(html, pdf_path):
    """Render HTML to paginated PDF via WeasyPrint."""
    doc = weasyprint.HTML(string=html)
    doc.write_pdf(str(pdf_path))


def pdf_to_images(pdf_path, out_dir, stem, dpi=DPI):
    """Convert each PDF page to a PNG image."""
    doc = fitz.open(str(pdf_path))
    paths = []
    for i, page in enumerate(doc):
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        out_path = out_dir / f"{stem}_p{i+1}.png"
        pix.save(str(out_path))
        paths.append(out_path)
        print(f"Saved: {out_path}")
    doc.close()
    print(f"\nTotal: {len(paths)} pages")
    return paths


def main():
    if len(sys.argv) < 2:
        print("Usage: md2img.py <input.md> [output_dir] [--tldr 'custom tldr text']")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    md_text = md_path.read_text("utf-8")
    html = md_to_html(md_text)

    # Write intermediate files for debugging
    pdf_path = out_dir / f"{md_path.stem}.pdf"
    html_to_pdf(html, pdf_path)
    print(f"PDF: {pdf_path}")

    pdf_to_images(pdf_path, out_dir, md_path.stem)


if __name__ == "__main__":
    main()
