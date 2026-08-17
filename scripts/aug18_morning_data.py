"""8/17 종가 · 8/18 오전 Quick 코멘트 숫자 (원문 기준).

원문 타임스탬프: 06:45 / 06:52 / 06:54 / 06:55 / 07:01
숫자는 공개 코멘트 그대로 두고, 파생값만 검산한다.
"""

from __future__ import annotations

from dataclasses import dataclass


# ── 원문 입력 ──────────────────────────────────────────────
ASOF_US = "2026-08-17"
FX_KRW = 1417  # 원/달러
ADR_PER_LOCAL = 10  # 171.38달러 × 10 × 1,417원 ≈ 243만원

US = {
    "dow": -0.51,
    "spx": -0.52,
    "ndx": -0.32,
    "brent": 90.87,
    "brent_chg": 2.7,
    "ust30": 5.31,
    "ust10": 4.725,
    "sox_1d": 1.6,  # 06:52 코멘트 (당일)
    "micron_chg": 4.0,
}

KOREA_2D = {  # 8/14 + 8/17
    "ewy": 3.6,
    "hynix_adr": 3.4,
    "sox": 1.3,
    "kospi_baseline": 1.5,  # +1% 중반
}

HYNIX = {
    "local_man": 164.5,  # 만원
    "eps_26k": 346,  # 천원
    "eps_27k": 437,
    "op_26t": 266,  # 조원
    "op_27t": 392,
    "per_26": 4.8,
    "per_27": 3.8,
    "adr_usd": 171.38,
    "adr_krw_man_stated": 243,
    "adr_per_26": 7.0,
    "adr_per_27": 5.56,
    "adr_vs_micron_pct": -18,
    "adr_vs_local_premium_pct": 48,
}

SAMSUNG = {
    "local_man": 27.45,
    "eps_26k": 47.9,
    "eps_27k": 67.2,
    "op_26t": 391,
    "op_27t": 549,
    "per_26": 5.7,
    "per_27": 4.1,
}

MICRON = {
    "px": 1011.75,
    "fwd12_per": 8.1,
    "cy27_eps": 150,
    "cy27_per": 6.75,
}

SANDISK = {
    "px": 1786.85,
    "q1_eps": 45.0,
    "fy27_eps": 201,
    "fy27_per": 8.9,
}

WD = {
    "px": 536.01,
    "q1_eps": 4.0,
    "fy27_eps": 17.9,
    "fy27_per": 30,
}

SEAGATE = {
    "px": 994.79,
    "q1_eps": 7.3,
    "fy27_eps": 32.6,
    "fy27_per": 31,
}

# QoQ 사다리: +10%, +5%, +5%
QOQ = (0.10, 0.05, 0.05)

# 목표가 시나리오 (원문)
HYNIX_TP = {
    "recent_premium": (180, 187),  # 30~35%
    "normal_premium": 203,  # +20% (TSMC ~15%)
    "per6": 208,
    "per7": 242,
}
SAMSUNG_TP = {
    "same_flow": 30.0,  # 최근 프리미엄 감안 흐름
    "per6": 28.7,
    "per7": 33.5,
}

MONITOR = [
    ("유가", "$90 → $100 여부"),
    ("30년물", "5.3% → 5.5% 여부"),
    ("FOMC", "7월 의사록"),
    ("소비", "월마트 실적 → 미국 소비 확인"),
]


@dataclass(frozen=True)
class Check:
    name: str
    got: float
    stated: float
    tol: float
    unit: str = ""

    @property
    def ok(self) -> bool:
        return abs(self.got - self.stated) <= self.tol

    def line(self) -> str:
        mark = "OK" if self.ok else "FAIL"
        return f"[{mark}] {self.name}: got={self.got:.4f} stated={self.stated:.4f} tol={self.tol} {self.unit}"


def qoq_fy_eps(q1: float, qoq: tuple[float, float, float] = QOQ) -> float:
    q2 = q1 * (1 + qoq[0])
    q3 = q2 * (1 + qoq[1])
    q4 = q3 * (1 + qoq[2])
    return q1 + q2 + q3 + q4


def implied_per(price: float, eps: float) -> float:
    return price / eps


def adr_to_local_man(adr_usd: float, fx: float = FX_KRW, ratio: int = ADR_PER_LOCAL) -> float:
    """ADR 달러가 → 본주 환산 만원."""
    return adr_usd * fx * ratio / 10_000


def local_per(price_man: float, eps_k: float) -> float:
    """가격(만원) / EPS(천원) = 배."""
    return (price_man * 10) / eps_k


def implied_local_from_premium(adr_man: float, premium: float) -> float:
    return adr_man / (1 + premium)


def conservative_tp(eps_k: float, per: float) -> float:
    """26년 EPS(천원) × PER → 만원."""
    return eps_k * per / 10


def checks() -> list[Check]:
    adr_man = adr_to_local_man(HYNIX["adr_usd"])
    premium = adr_man / HYNIX["local_man"] - 1
    vs_mu = HYNIX["adr_per_27"] / MICRON["cy27_per"] - 1
    sndk_eps = qoq_fy_eps(SANDISK["q1_eps"])
    wd_eps = qoq_fy_eps(WD["q1_eps"])
    stx_eps = qoq_fy_eps(SEAGATE["q1_eps"])
    samsung_same = HYNIX["local_man"] and (
        SAMSUNG["local_man"] * (HYNIX_TP["recent_premium"][0] / HYNIX["local_man"])
    )

    return [
        Check("하이닉스 본주 26년 PER", local_per(HYNIX["local_man"], HYNIX["eps_26k"]), HYNIX["per_26"], 0.06),
        Check("하이닉스 본주 27년 PER", local_per(HYNIX["local_man"], HYNIX["eps_27k"]), HYNIX["per_27"], 0.06),
        Check("삼성전자 26년 PER", local_per(SAMSUNG["local_man"], SAMSUNG["eps_26k"]), SAMSUNG["per_26"], 0.06),
        Check("삼성전자 27년 PER", local_per(SAMSUNG["local_man"], SAMSUNG["eps_27k"]), SAMSUNG["per_27"], 0.06),
        Check("ADR→본주 환산(만원)", adr_man, HYNIX["adr_krw_man_stated"], 0.4, "만원"),
        Check("ADR 본주 대비 프리미엄", premium * 100, HYNIX["adr_vs_local_premium_pct"], 1.0, "%"),
        Check("정상 +20% 시 본주", implied_local_from_premium(HYNIX["adr_krw_man_stated"], 0.20), HYNIX_TP["normal_premium"], 0.6, "만원"),
        Check("프리미엄 +30% 시 본주", implied_local_from_premium(HYNIX["adr_krw_man_stated"], 0.30), HYNIX_TP["recent_premium"][1], 0.6, "만원"),
        Check("프리미엄 +35% 시 본주", implied_local_from_premium(HYNIX["adr_krw_man_stated"], 0.35), HYNIX_TP["recent_premium"][0], 0.6, "만원"),
        Check("마이크론 CY27 PER", implied_per(MICRON["px"], MICRON["cy27_eps"]), MICRON["cy27_per"], 0.02),
        Check("하이닉스ADR vs 마이크론 CY27", vs_mu * 100, HYNIX["adr_vs_micron_pct"], 1.0, "%"),
        Check("Sandisk FY27 EPS", sndk_eps, SANDISK["fy27_eps"], 0.6, "달러"),
        Check("Sandisk FY27 PER", implied_per(SANDISK["px"], SANDISK["fy27_eps"]), SANDISK["fy27_per"], 0.15),
        Check("WD FY27 EPS", wd_eps, WD["fy27_eps"], 0.15, "달러"),
        Check("WD FY27 PER", implied_per(WD["px"], WD["fy27_eps"]), WD["fy27_per"], 0.2),
        Check("Seagate FY27 EPS", stx_eps, SEAGATE["fy27_eps"], 0.15, "달러"),
        Check("Seagate FY27 PER", implied_per(SEAGATE["px"], SEAGATE["fy27_eps"]), SEAGATE["fy27_per"], 0.6),
        Check("하이닉스 PER6 목표가", conservative_tp(HYNIX["eps_26k"], 6), HYNIX_TP["per6"], 0.6, "만원"),
        Check("하이닉스 PER7 목표가", conservative_tp(HYNIX["eps_26k"], 7), HYNIX_TP["per7"], 0.6, "만원"),
        Check("삼성전자 PER6 목표가", conservative_tp(SAMSUNG["eps_26k"], 6), SAMSUNG_TP["per6"], 0.15, "만원"),
        Check("삼성전자 PER7 목표가", conservative_tp(SAMSUNG["eps_26k"], 7), SAMSUNG_TP["per7"], 0.15, "만원"),
        Check("삼전 같은흐름(180만 기준)", samsung_same, SAMSUNG_TP["same_flow"], 0.2, "만원"),
    ]


def assert_all() -> list[Check]:
    rows = checks()
    bad = [c for c in rows if not c.ok]
    if bad:
        detail = "\n".join(c.line() for c in bad)
        raise AssertionError(f"{len(bad)} number check(s) failed:\n{detail}")
    return rows


if __name__ == "__main__":
    for c in checks():
        print(c.line())
    assert_all()
    print("all checks passed")
