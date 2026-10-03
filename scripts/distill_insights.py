#!/usr/bin/env python3
"""투자 코멘트 원문을 읽어 증류 노트(md, json, docx)를 만든다."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from insight_distiller.__main__ import main

if __name__ == "__main__":
    main()
