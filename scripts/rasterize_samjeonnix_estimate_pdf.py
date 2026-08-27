#!/usr/bin/env python3
"""Rasterize the 삼전닉스 estimate PDF."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "reports" / "2026-08-27-samjeonnix-estimate.pdf"
OUT = ROOT / "reports" / "samjeonnix-estimate" / "pdf-pages"
HTML = ROOT / "reports" / "2026-08-27-samjeonnix-estimate-pages.html"


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"missing {PDF}")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("page*.png"):
        old.unlink()
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise SystemExit("pdftoppm required")
    subprocess.run([pdftoppm, "-png", "-r", "140", str(PDF), str(OUT / "page")], check=True)
    pages = sorted(OUT.glob("page-*.png")) or sorted(OUT.glob("page*.png"))
    renamed = []
    for i, p in enumerate(sorted(pages), 1):
        dest = OUT / f"page-{i:02d}.png"
        if p.resolve() != dest.resolve():
            if dest.exists():
                dest.unlink()
            p.rename(dest)
        renamed.append(dest)
    imgs = "\n".join(
        f'    <figure><img src="samjeonnix-estimate/pdf-pages/{p.name}" alt="page {i}" /><figcaption>{i} / {len(renamed)}</figcaption></figure>'
        for i, p in enumerate(renamed, 1)
    )
    HTML.write_text(
        f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>삼전닉스 실적 추정 · 페이지</title>
<style>
body {{ margin: 0; background: #1a1f2b; color: #d7deea; font-family: "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
header {{ max-width: 920px; margin: 0 auto; padding: 18px 16px 8px; }}
h1 {{ font-size: 20px; margin: 0 0 6px; color: #fff; }}
a {{ color: #f3d48a; }}
figure {{ margin: 0 auto 18px; max-width: 920px; }}
img {{ width: 100%; background: #fff; border-radius: 8px; display: block; }}
figcaption {{ text-align: center; font-size: 12px; margin-top: 6px; opacity: .7; }}
</style></head><body>
<header><h1>삼전닉스 실적 추정 · {len(renamed)}쪽</h1>
<p>원문: <a href="2026-08-27-samjeonnix-estimate.html">HTML</a></p></header>
{imgs}
</body></html>
""",
        encoding="utf-8",
    )
    print(f"rasterized {len(renamed)} pages")


if __name__ == "__main__":
    main()
