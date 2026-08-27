#!/usr/bin/env python3
"""Rasterize the A4 PDF so the briefing opens without a PDF app."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "reports" / "2026-08-27-nvda-q2-call-analysis.pdf"
OUT = ROOT / "reports" / "nvda-q2-call" / "pdf-pages"
HTML = ROOT / "reports" / "2026-08-27-nvda-q2-call-pages.html"


def _pages() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("page-*.png"):
        old.unlink()
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        subprocess.run(
            [pdftoppm, "-png", "-r", "140", str(PDF), str(OUT / "page")],
            check=True,
        )
        pages = sorted(OUT.glob("page-*.png")) or sorted(OUT.glob("page*.png"))
        # pdftoppm names page-1.png or page-01.png depending on count
        renamed = []
        for i, p in enumerate(sorted(pages), 1):
            dest = OUT / f"page-{i:02d}.png"
            if p != dest:
                p.rename(dest)
            renamed.append(dest)
        return renamed

    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(PDF))
    paths = []
    for i, page in enumerate(doc, 1):
        dest = OUT / f"page-{i:02d}.png"
        bitmap = page.render(scale=140 / 72)
        bitmap.to_pil().save(dest, "PNG")
        paths.append(dest)
    return paths


def _write_html(pages: list[Path]) -> None:
    imgs = "\n".join(
        f'    <figure><img src="nvda-q2-call/pdf-pages/{p.name}" alt="page {i}" /><figcaption>{i} / {len(pages)}</figcaption></figure>'
        for i, p in enumerate(pages, 1)
    )
    HTML.write_text(
        f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>엔비디아 FY27 2Q 컨콜 분석 · 페이지</title>
  <style>
    body {{ margin: 0; background: #1a1f2b; color: #d7deea; font-family: "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
    header {{ max-width: 920px; margin: 0 auto; padding: 18px 16px 8px; }}
    h1 {{ font-size: 20px; margin: 0 0 6px; color: #fff; }}
    a {{ color: #f3d48a; }}
    figure {{ margin: 0 auto 18px; max-width: 920px; }}
    img {{ width: 100%; background: #fff; border-radius: 8px; display: block; }}
    figcaption {{ text-align: center; font-size: 12px; margin-top: 6px; opacity: .7; }}
  </style>
</head>
<body>
  <header>
    <h1>엔비디아 FY27 2Q 컨콜 분석 · {len(pages)}쪽</h1>
    <p>PDF가 안 열리면 이 페이지. 원문 HTML: <a href="2026-08-27-nvda-q2-call-analysis.html">2026-08-27-nvda-q2-call-analysis.html</a></p>
  </header>
{imgs}
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"missing {PDF}")
    pages = _pages()
    if not pages:
        raise SystemExit("no pages rasterized")
    _write_html(pages)
    print(f"rasterized {len(pages)} pages → {OUT}")
    print(f"wrote {HTML}")


if __name__ == "__main__":
    main()
