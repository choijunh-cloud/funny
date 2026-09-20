#!/usr/bin/env python3
"""차트 + 한 장 + 장문 + 마크다운을 한 번에 만든다."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT / "scripts"))

import insights_charts  # noqa: E402
import generate_insights_html  # noqa: E402
import generate_insights_oneboard  # noqa: E402
import generate_insights_md  # noqa: E402


def main() -> None:
    paths = insights_charts.render_all()
    print(f"charts {len(paths)}")
    p1 = generate_insights_oneboard.write()
    p2 = generate_insights_html.write()
    p3 = generate_insights_md.write()
    print(p1)
    print(p2)
    print(p3)


if __name__ == "__main__":
    main()
