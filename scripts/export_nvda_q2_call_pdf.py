#!/usr/bin/env python3
"""Export the NVIDIA Q2 call analysis HTML to A4 PDF via Chrome headless."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "reports" / "2026-08-27-nvda-q2-call-analysis.html"
PDF = ROOT / "reports" / "2026-08-27-nvda-q2-call-analysis.pdf"
SHARE = ROOT / "lectures" / "8월 27일 NVIDIA Q2 FY2027 컨콜 분석.pdf"
CHROME = shutil.which("google-chrome") or shutil.which("google-chrome-stable") or "google-chrome"


def main() -> None:
    if not HTML.exists():
        raise SystemExit(f"missing {HTML}")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    SHARE.parent.mkdir(parents=True, exist_ok=True)
    profile = Path("/tmp/chrome-nvda-call-pdf-profile")
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
        f"--print-to-pdf={PDF}",
        "--virtual-time-budget=12000",
        HTML.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, check=False, timeout=120)
    except subprocess.TimeoutExpired:
        pass
    if not PDF.exists() or PDF.stat().st_size < 10_000:
        raise SystemExit(f"PDF not created: {PDF}")
    SHARE.write_bytes(PDF.read_bytes())
    print(f"wrote {PDF} ({PDF.stat().st_size} bytes)")
    print(f"wrote {SHARE}")


if __name__ == "__main__":
    main()
