#!/usr/bin/env python3
"""Rasterize the broadcast A4 PDF so it opens without a PDF app."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "reports" / "2026-08-28-broadcast-brief.pdf"
OUT = ROOT / "reports" / "broadcast-pages"
HTML = ROOT / "reports" / "2026-08-28-broadcast-brief-pages.html"

TITLES = [
    "표지 · 한 줄",
    "채널 맵",
    "타임코드",
    "ASR · 라디오 금리",
    "라디오 환율·주식",
    "박세익",
    "문남중 · 이영수",
    "케스닥 · 박근형",
    "교차표",
    "엔비디아 동기화",
    "9월 전략",
]


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
    nav = "".join(f'<a href="#p{i}">{i}</a>' for i in range(1, len(pages) + 1))
    articles = []
    for i, p in enumerate(pages, 1):
        title = TITLES[i - 1] if i - 1 < len(TITLES) else "이어짐"
        articles.append(
            f'    <article class="page" id="p{i}">'
            f"<h2>{i} / {len(pages)} · {title}</h2>"
            f'<img src="broadcast-pages/{p.name}" alt="{i}쪽 {title}" /></article>'
        )
    HTML.write_text(
        f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>8월 28일 방송 코멘트 · PDF 페이지</title>
  <style>
    :root {{ --navy: #0f2043; --gold: #b8943a; --bg: #e8ebf2; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "WenQuanYi Micro Hei", sans-serif;
      color: #1a1a1a;
    }}
    .top {{
      position: sticky; top: 0; z-index: 20;
      background: var(--navy); color: #fff;
      box-shadow: 0 2px 10px rgba(15,32,67,.18);
    }}
    .top-inner {{ max-width: 860px; margin: 0 auto; padding: 10px 14px 12px; }}
    .brand {{ font-size: 13px; }}
    .brand b {{ font-size: 15px; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }}
    nav a {{
      color: #dbe4f5; text-decoration: none; font-size: 12px; font-weight: 700;
      min-width: 28px; text-align: center;
      padding: 3px 7px; border-radius: 999px; background: rgba(255,255,255,.08);
    }}
    nav a:hover {{ background: var(--gold); color: var(--navy); }}
    .wrap {{ max-width: 860px; margin: 0 auto; padding: 16px 12px 64px; }}
    h1 {{ font-size: 22px; color: var(--navy); margin: 8px 0 6px; }}
    .muted {{ color: #4b5563; font-size: 13px; margin: 0 0 16px; }}
    .page {{
      background: #fff; border-radius: 10px; margin: 18px 0;
      border: 1px solid #d7deea; overflow: hidden;
    }}
    .page h2 {{
      margin: 0; padding: 8px 12px; font-size: 13px;
      background: var(--navy); color: #fff;
    }}
    .page img {{ display: block; width: 100%; height: auto; }}
  </style>
</head>
<body>
  <div class="top">
    <div class="top-inner">
      <div class="brand">BROADCAST BRIEF · PDF 페이지 · <b>8월 28일</b></div>
      <nav>
        {nav}
        <a href="2026-08-28-broadcast-brief.html">HTML</a>
      </nav>
    </div>
  </div>
  <div class="wrap">
    <h1>A4 {len(pages)}쪽 · 방송 시간 동기화</h1>
    <p class="muted">PDF 앱이 없어도 됩니다. 매수·매도 추천 아님. ASR 교정본.</p>
{chr(10).join(articles)}
  </div>
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
