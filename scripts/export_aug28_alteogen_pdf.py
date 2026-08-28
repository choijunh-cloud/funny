#!/usr/bin/env python3
"""Export the Aug 28 Alteogen briefing HTML to A4 PDF via Chrome headless."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "reports" / "2026-08-28-alteogen-alt-b4.html"
PDF = ROOT / "reports" / "2026-08-28-alteogen-alt-b4.pdf"
SHARE = ROOT / "lectures" / "8월 28일 알테오젠 ALT-B4 분석.pdf"
CORE_HTML = ROOT / "reports" / "2026-08-28-alteogen-alt-b4-core.html"
CORE_PDF = ROOT / "reports" / "2026-08-28-alteogen-alt-b4-core.pdf"
CORE_SHARE = ROOT / "lectures" / "8월 28일 알테오젠 ALT-B4 핵심요약.pdf"
CHROME = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or "google-chrome"


def _print(html: Path, pdf: Path, share: Path, profile_name: str) -> None:
    if not html.exists():
        raise SystemExit(f"missing {html}")
    pdf.parent.mkdir(parents=True, exist_ok=True)
    share.parent.mkdir(parents=True, exist_ok=True)
    profile = Path(f"/tmp/{profile_name}")
    profile.mkdir(parents=True, exist_ok=True)
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-extensions",
        "--disable-default-apps",
        "--disable-component-update",
        "--no-first-run",
        "--hide-scrollbars",
        "--no-pdf-header-footer",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf}",
        "--virtual-time-budget=5000",
        html.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, check=False, timeout=45)
    except subprocess.TimeoutExpired:
        pass
    if not pdf.exists() or pdf.stat().st_size < 10_000:
        raise SystemExit(f"PDF not created: {pdf}")
    share.write_bytes(pdf.read_bytes())
    print(f"wrote {pdf} ({pdf.stat().st_size} bytes)")
    print(f"wrote {share}")


def main() -> None:
    _print(HTML, PDF, SHARE, "chrome-aug28-alteogen-pdf")
    _print(CORE_HTML, CORE_PDF, CORE_SHARE, "chrome-aug28-alteogen-core-pdf")


if __name__ == "__main__":
    main()
