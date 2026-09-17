#!/usr/bin/env python3
"""한 장 보드를 기본 HTML 경로에도 같이 쓴다."""

from __future__ import annotations

import shutil
from pathlib import Path

from generate_sep17_oneboard import OUT as ONEBOARD
from generate_sep17_oneboard import main as build_oneboard

ALIAS = Path("/workspace/lectures/9월 17일 AI·반도체 시장 코멘트.html")


def main() -> None:
    build_oneboard()
    shutil.copyfile(ONEBOARD, ALIAS)
    print(f"Copied {ONEBOARD.name} -> {ALIAS.name}")


if __name__ == "__main__":
    main()
