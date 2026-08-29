#!/usr/bin/env python3
"""Make briefs openable: image PDFs + markdown/HTML page viewers.

Cursor and GitHub open .pdf as source (%PDF-1.4). Markdown preview and
PNG page viewers actually show the pages. Pillow image-PDFs open in
Preview / Acrobat / Chrome after download.
"""

from __future__ import annotations

import html
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
LECTURES = ROOT / "lectures"

QUICK_PDF = REPORTS / "2026-08-28-quick-comment-brief.pdf"
CORE_PDF = REPORTS / "2026-08-28-quick-comment-core.pdf"
BROAD_PDF = REPORTS / "2026-08-28-broadcast-brief.pdf"

QUICK_PAGES = REPORTS / "pdf-pages"
CORE_PAGES = REPORTS / "core-pages"
BROAD_PAGES = REPORTS / "broadcast-pages"

QUICK_TITLES = [
    "표지 · KPI",
    "한 줄",
    "엔비디아 실적",
    "가이던스 · Rubin",
    "72~73% · 525조",
    "네트워크 칩",
    "메모리 밸류",
    "마이크론 SCA",
    "KV Cache · 마벨",
    "미국 · 국내",
    "전력 · BBU",
    "관세 · SKT",
    "화장품",
    "옆 테마",
    "포트 · 관심주",
    "체크 · 원문",
]
BROAD_TITLES = [
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
    "이어짐",
    "이어짐",
]
CORE_TITLES = ["핵심요약 1", "핵심요약 2"]


def rasterize(pdf: Path, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("page-*.png"):
        old.unlink()
    doc = pdfium.PdfDocument(str(pdf))
    paths = []
    for i, page in enumerate(doc, 1):
        dest = out_dir / f"page-{i:02d}.png"
        page.render(scale=140 / 72).to_pil().save(dest, "PNG", optimize=True)
        paths.append(dest)
    if not paths:
        raise SystemExit(f"no pages from {pdf}")
    print(f"rasterized {len(paths)} → {out_dir}")
    return paths


def pngs(folder: Path) -> list[Path]:
    pages = sorted(folder.glob("page-*.png"))
    if not pages:
        raise SystemExit(f"missing pngs in {folder}")
    return pages


def rebuild_pdf(pages: list[Path], dest: Path, share: Path | None = None) -> None:
    images = [Image.open(p).convert("RGB") for p in pages]
    dest.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        dest,
        save_all=True,
        append_images=images[1:],
        format="PDF",
        resolution=140.0,
    )
    for im in images:
        im.close()
    if share is not None:
        share.parent.mkdir(parents=True, exist_ok=True)
        share.write_bytes(dest.read_bytes())
        print(f"wrote {dest} ({dest.stat().st_size} bytes) and {share.name}")
    else:
        print(f"wrote {dest} ({dest.stat().st_size} bytes)")


def title_of(titles: list[str], i: int, n: int) -> str:
    if i - 1 < len(titles):
        t = titles[i - 1]
        if i == n and n > len(titles):
            return "원문 부록"
        return t
    return "원문 부록" if i == n else "이어짐"


def write_md(
    path: Path,
    heading: str,
    intro: str,
    pages: list[Path],
    rel_prefix: str,
    titles: list[str],
    extra: str = "",
) -> None:
    n = len(pages)
    blocks = [
        f"# {heading}\n",
        "> **PDF를 Cursor에서 열면 `%PDF-1.4` 코드처럼 보입니다.** 이 마크다운을 열면 페이지가 그림으로 보입니다. GitHub에서도 그림이 바로 나옵니다.\n",
        intro.rstrip() + "\n",
    ]
    if extra.strip():
        blocks.append(extra.strip() + "\n")
    blocks.append(f"## 페이지 그림 ({n}쪽)\n")
    blocks.append("매수·매도 권유가 아닙니다.\n")
    for i, p in enumerate(pages, 1):
        title = title_of(titles, i, n)
        blocks.append(f"### {i}쪽 · {title}\n")
        blocks.append(f"![{i}쪽 {title}]({rel_prefix}/{p.name})\n")
    path.write_text("\n".join(blocks), encoding="utf-8")
    print(f"wrote {path}")


def write_html(path: Path, heading: str, pages: list[Path], rel_prefix: str, titles: list[str], extra_nav: str) -> None:
    n = len(pages)
    nav = "".join(f'<a href="#p{i}">{i}</a>' for i in range(1, n + 1))
    articles = []
    for i, p in enumerate(pages, 1):
        title = html.escape(title_of(titles, i, n))
        articles.append(
            f'<article class="page" id="p{i}"><h2>{i} / {n} · {title}</h2>'
            f'<img src="{html.escape(rel_prefix)}/{p.name}" alt="{i}쪽 {title}" /></article>'
        )
    path.write_text(
        f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(heading)}</title>
  <style>
    :root {{ --navy: #0f2043; --gold: #b8943a; --bg: #e8ebf2; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; background: var(--bg);
      font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif; color: #1a1a1a; }}
    .top {{ position: sticky; top: 0; z-index: 20; background: var(--navy); color: #fff; }}
    .top-inner {{ max-width: 860px; margin: 0 auto; padding: 10px 14px 12px; }}
    nav {{ display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }}
    nav a {{ color: #dbe4f5; text-decoration: none; font-size: 12px; font-weight: 700;
      min-width: 28px; text-align: center; padding: 3px 7px; border-radius: 999px; background: rgba(255,255,255,.08); }}
    .wrap {{ max-width: 860px; margin: 0 auto; padding: 16px 12px 64px; }}
    h1 {{ font-size: 22px; color: var(--navy); }}
    .muted {{ color: #4b5563; font-size: 13px; }}
    .page {{ background: #fff; border-radius: 10px; margin: 18px 0; border: 1px solid #d7deea; overflow: hidden; }}
    .page h2 {{ margin: 0; padding: 8px 12px; font-size: 13px; background: var(--navy); color: #fff; }}
    .page img {{ display: block; width: 100%; height: auto; }}
  </style>
</head>
<body>
  <div class="top"><div class="top-inner">
    <div><b>{html.escape(heading)}</b> · PDF 대신 이 파일을 브라우저로 여세요</div>
    <nav>{nav}{extra_nav}</nav>
  </div></div>
  <div class="wrap">
    <h1>{html.escape(heading)} · {n}쪽</h1>
    <p class="muted">Cursor에서 PDF는 코드처럼 보입니다. 이 HTML은 브라우저에서 페이지 그림으로 열립니다. 매수·매도 권유 아님.</p>
    {"".join(articles)}
  </div>
</body>
</html>
""",
        encoding="utf-8",
    )
    print(f"wrote {path}")


OPENER = """# 여기서 보세요

Cursor와 GitHub는 `.pdf`를 문서가 아니라 **소스 코드**(`%PDF-1.4`)로 엽니다. 아래 **마크다운**을 열면 페이지가 그림으로 보입니다.

1. [Quick 코멘트 시각화 47쪽](lectures/8월%2028일%20Quick%20코멘트%20시각화.md)
2. [Quick 코멘트 핵심요약](lectures/8월%2028일%20Quick%20코멘트%20핵심요약.md)
3. [방송 코멘트 13쪽](lectures/8월%2028일%20방송%20코멘트%20정리.md)

브라우저로 보려면 `reports/` 아래 `*-pages.html` 또는 `lectures/` 아래 같은 이름 `.html`을 여세요.

내려받은 PDF는 미리보기/Acrobat/Chrome에서 열립니다. 이 저장소 안에서 `.pdf`를 클릭하면 코드처럼 보이는 것이 정상입니다.

매수·매도 권유가 아닙니다.
"""

OPENER_LECTURES = """# 여기서 보세요

Cursor에서 `.pdf`를 열면 `%PDF-1.4` 코드처럼 보입니다. **아래 마크다운**을 여세요.

1. [Quick 코멘트 시각화 47쪽](8월%2028일%20Quick%20코멘트%20시각화.md)
2. [Quick 코멘트 핵심요약](8월%2028일%20Quick%20코멘트%20핵심요약.md)
3. [방송 코멘트 13쪽](8월%2028일%20방송%20코멘트%20정리.md)

같은 이름 `.html`은 브라우저용입니다.

매수·매도 권유가 아닙니다.
"""


def main() -> None:
    if not QUICK_PAGES.exists() or not list(QUICK_PAGES.glob("page-*.png")):
        rasterize(QUICK_PDF, QUICK_PAGES)
    if not BROAD_PAGES.exists() or not list(BROAD_PAGES.glob("page-*.png")):
        rasterize(BROAD_PDF, BROAD_PAGES)
    rasterize(CORE_PDF, CORE_PAGES)

    quick = pngs(QUICK_PAGES)
    core = pngs(CORE_PAGES)
    broad = pngs(BROAD_PAGES)

    rebuild_pdf(quick, QUICK_PDF, LECTURES / "8월 28일 Quick 코멘트 시각화.pdf")
    rebuild_pdf(core, CORE_PDF, LECTURES / "8월 28일 Quick 코멘트 핵심요약.pdf")
    rebuild_pdf(broad, BROAD_PDF, LECTURES / "8월 28일 방송 코멘트 정리.pdf")

    core_src = (LECTURES / "8월 28일 Quick 코멘트 핵심요약.md").read_text(encoding="utf-8")
    broad_src = (LECTURES / "8월 28일 방송 코멘트 정리.md").read_text(encoding="utf-8")
    for marker in ("\n## 페이지 그림", "\n### 1쪽 ·"):
        core_src = core_src.split(marker)[0]
        broad_src = broad_src.split(marker)[0]
    core_extra = "\n".join(core_src.splitlines()[1:]).strip()
    broad_extra = "\n".join(broad_src.splitlines()[1:]).strip()

    write_md(
        LECTURES / "8월 28일 Quick 코멘트 시각화.md",
        "8월 28일 Quick 코멘트 시각화",
        "8/27 저녁~8/28 오후 Quick 코멘트와 첨부 PDF 5건. 원문은 뒤쪽 부록 쪽.",
        quick,
        "../reports/pdf-pages",
        QUICK_TITLES,
    )
    write_md(
        LECTURES / "8월 28일 Quick 코멘트 핵심요약.md",
        "8월 28일 Quick 코멘트 핵심요약",
        "+70%는 수요 상한이 아니라 공급 상한. 525조 = 엔비디아 315 + HBM 81 + 잔여 130. 스윙은 비CSP.",
        core,
        "../reports/core-pages",
        CORE_TITLES,
        extra=core_extra,
    )
    write_md(
        LECTURES / "8월 28일 방송 코멘트 정리.md",
        "8월 28일 방송 코멘트 정리",
        "KBS·채슬리·대신·아신·케스닥·IBK를 타임코드로 묶고 Quick PDF와 교차.",
        broad,
        "../reports/broadcast-pages",
        BROAD_TITLES,
        extra=broad_extra,
    )

    write_html(
        REPORTS / "2026-08-28-quick-comment-brief-pages.html",
        "8월 28일 Quick 코멘트",
        quick,
        "pdf-pages",
        QUICK_TITLES,
        '<a href="열어보기.md">안내</a>',
    )
    write_html(
        REPORTS / "2026-08-28-quick-comment-core-pages.html",
        "8월 28일 핵심요약",
        core,
        "core-pages",
        CORE_TITLES,
        '<a href="열어보기.md">안내</a>',
    )
    write_html(
        REPORTS / "2026-08-28-broadcast-brief-pages.html",
        "8월 28일 방송 코멘트",
        broad,
        "broadcast-pages",
        BROAD_TITLES,
        '<a href="열어보기.md">안내</a>',
    )
    write_html(
        LECTURES / "8월 28일 Quick 코멘트 시각화.html",
        "8월 28일 Quick 코멘트",
        quick,
        "../reports/pdf-pages",
        QUICK_TITLES,
        '<a href="열어보기.md">안내</a>',
    )
    write_html(
        LECTURES / "8월 28일 Quick 코멘트 핵심요약.html",
        "8월 28일 핵심요약",
        core,
        "../reports/core-pages",
        CORE_TITLES,
        '<a href="열어보기.md">안내</a>',
    )
    write_html(
        LECTURES / "8월 28일 방송 코멘트 정리.html",
        "8월 28일 방송 코멘트",
        broad,
        "../reports/broadcast-pages",
        BROAD_TITLES,
        '<a href="열어보기.md">안내</a>',
    )

    (ROOT / "열어보기.md").write_text(OPENER, encoding="utf-8")
    (LECTURES / "열어보기.md").write_text(OPENER_LECTURES, encoding="utf-8")
    (REPORTS / "열어보기.md").write_text(
        """# 여기서 보세요

Cursor에서 `.pdf`를 열면 `%PDF-1.4` 코드처럼 보입니다. **아래 마크다운**을 여세요.

1. [Quick 코멘트 시각화 47쪽](../lectures/8월%2028일%20Quick%20코멘트%20시각화.md)
2. [Quick 코멘트 핵심요약](../lectures/8월%2028일%20Quick%20코멘트%20핵심요약.md)
3. [방송 코멘트 13쪽](../lectures/8월%2028일%20방송%20코멘트%20정리.md)

이 폴더의 `*-pages.html`은 브라우저용입니다.

매수·매도 권유가 아닙니다.
""",
        encoding="utf-8",
    )
    print("wrote 열어보기.md")


if __name__ == "__main__":
    main()
