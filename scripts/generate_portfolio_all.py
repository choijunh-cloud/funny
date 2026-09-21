#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_portfolio_html
import portfolio_charts


def main() -> None:
    for p in portfolio_charts.render_all():
        print(p)
    a, b = generate_portfolio_html.write()
    print(a)
    print(b)


if __name__ == "__main__":
    main()
