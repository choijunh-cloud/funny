#!/usr/bin/env python3
"""10/7 증류 엔트리 — 정량 모델 결과를 채팅/MD로 렌더."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oct7_model as model


def main() -> None:
    model.main()


if __name__ == "__main__":
    main()
