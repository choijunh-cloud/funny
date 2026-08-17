"""금액 단위 헬퍼.

모델 내부의 모든 금액은 **만원** 단위 float 이다.
    1억 = 10,000 만원, 90억 = 900,000 만원
세법 구간(1,400만 / 5,000만 / 8,800만 ...)이 만원 단위로 딱 떨어지기 때문에
내부 단위를 만원으로 고정한다.
"""

from __future__ import annotations

EOK = 10_000.0  # 1억 = 10,000만원
MAN = 1.0


def to_eok(manwon: float) -> float:
    return manwon / EOK


def from_eok(eok: float) -> float:
    return eok * EOK


def fmt_eok(manwon: float, digits: int = 2) -> str:
    return f"{manwon / EOK:,.{digits}f}억"


def fmt_man(manwon: float, digits: int = 0) -> str:
    return f"{manwon:,.{digits}f}만"


def fmt_signed_eok(manwon: float, digits: int = 1) -> str:
    sign = "+" if manwon >= 0 else "−"
    return f"{sign}{abs(manwon) / EOK:,.{digits}f}억"
