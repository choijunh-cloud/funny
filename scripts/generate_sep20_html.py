#!/usr/bin/env python3
"""상세 HTML 별칭. 시각화 보드와 같은 파일을 쓴다."""

import shutil
from pathlib import Path

from generate_sep20_oneboard import OUT as ONEBOARD
from generate_sep20_oneboard import main as build_oneboard

ALIAS = Path("/workspace/lectures/9월 20일 일요일 오전 다이제스트.html")


def main() -> None:
    build_oneboard()
    shutil.copyfile(ONEBOARD, ALIAS)
    print(f"Copied {ONEBOARD.name} -> {ALIAS.name}")


if __name__ == "__main__":
    main()
