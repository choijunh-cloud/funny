#!/usr/bin/env python3
"""8월 19일 강의노트에 쓰는 FCF·자사주 숫자 산술 검증."""

from __future__ import annotations


def main() -> None:
    assert 6452 * 62 == 400_024, "일매입 × 영업일 ≠ 약 40조(억원)"
    assert abs(400_024 / 10_000 - 40.0024) < 0.01

    assert 385 * 0.5 == 192.5
    assert 192.5 - 40 == 152.5

    assert 179 + 242 + 237 == 658
    assert 150 + 210 + 205 == 565

    # 보수 차감 밴드(원문: 연 20~30조)
    assert 179 - 150 == 29
    assert 242 - 210 == 32
    assert 237 - 205 == 32

    print("aug19 number checks OK")


if __name__ == "__main__":
    main()
