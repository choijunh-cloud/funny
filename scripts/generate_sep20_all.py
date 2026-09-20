#!/usr/bin/env python3
"""차트 → HTML → DOCX를 한 번에 만든다."""

from __future__ import annotations

from generate_sep20_brief import main as brief
from generate_sep20_html import main as html
from sep20_charts import main as charts


def main() -> None:
    charts()
    html()
    brief()


if __name__ == "__main__":
    main()
