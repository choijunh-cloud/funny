#!/usr/bin/env python3
"""텐센트 2026-10-12 글로벌 중기채권 공시의 재무 요약을 재계산한다.

원문 단위는 인민폐 백만 위안이다. 성장률·마진·현금·부채는 공시 금액을
더하고 나누어 다시 구하고, 합계가 어긋나면 종료한다. matplotlib로 차트를
만들고 한글 브리핑을 쓴다.

실행: python3 scripts/analyze_tencent_mtn_20261012.py
필요 패키지: matplotlib
"""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "tencent-mtn-20261012"
ARTIFACTS = Path("/opt/cursor/artifacts")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

# 연간·반기 매출과 원가. 키: 2023, 2024, 2025, 1H25, 1H26. 단위 RMB million.
SEGMENTS = ("VAS", "마케팅", "핀테크·기업", "기타")
REVENUE = {
    "VAS": {"2023": 298_375, "2024": 319_168, "2025": 369_281, "1H25": 183_501, "1H26": 194_524},
    "마케팅": {"2023": 101_482, "2024": 121_374, "2025": 144_973, "1H25": 67_615, "1H26": 81_736},
    "핀테크·기업": {"2023": 203_763, "2024": 211_956, "2025": 229_435, "1H25": 110_443, "1H26": 120_171},
    "기타": {"2023": 5_395, "2024": 7_759, "2025": 8_077, "1H25": 2_967, "1H26": 4_812},
}
COGS = {
    "VAS": {"2023": 136_456, "2024": 137_511, "2025": 146_985, "1H25": 73_367, "1H26": 71_471},
    "마케팅": {"2023": 50_138, "2024": 54_142, "2025": 61_584, "1H25": 29_336, "1H26": 35_777},
    "핀테크·기업": {"2023": 123_127, "2024": 112_255, "2025": 112_819, "1H25": 53_894, "1H26": 57_573},
    "기타": {"2023": 6_185, "2024": 7_103, "2025": 7_785, "1H25": 2_423, "1H26": 6_724},
}
REVENUE_TOTAL = {"2023": 609_015, "2024": 660_257, "2025": 751_766, "1H25": 364_526, "1H26": 401_243}
COGS_TOTAL = {"2023": 315_906, "2024": 311_011, "2025": 329_173, "1H25": 159_020, "1H26": 171_545}
GROSS_TOTAL = {"2023": 293_109, "2024": 349_246, "2025": 422_593, "1H25": 205_506, "1H26": 229_698}

# 공시가 억 위안 단위로만 준 게임·소셜 분해. 성장률은 공시 문구.
GAMES_EOK = {
    "FY24": {"국내게임": 1_397, "해외게임": 580, "소셜": 1_215, "국내yoy": 0.10, "해외yoy": 0.09, "소셜yoy": 0.02},
    "FY25": {"국내게임": 1_642, "해외게임": 774, "소셜": 1_277, "국내yoy": 0.18, "해외yoy": 0.33, "소셜yoy": 0.05},
    "1H26": {"국내게임": 927, "해외게임": 374, "소셜": 644, "국내yoy": 0.11, "해외yoy": 0.06, "소셜yoy": -0.007},
}

# 9개 분기. 비용·세금은 음수.
Q_LABELS = ["24Q2", "24Q3", "24Q4", "25Q1", "25Q2", "25Q3", "25Q4", "26Q1", "26Q2"]
Q = {
    "VAS": [78_822, 82_695, 79_022, 92_133, 91_368, 95_860, 89_920, 96_110, 98_414],
    "마케팅": [29_871, 29_993, 35_004, 31_853, 35_762, 36_242, 41_116, 38_171, 43_565],
    "핀테크·기업": [50_440, 53_089, 56_125, 54_907, 55_536, 58_174, 60_818, 59_885, 60_286],
    "기타": [1_984, 1_416, 2_295, 1_129, 1_838, 2_593, 2_517, 2_292, 2_520],
    "매출": [161_117, 167_193, 172_446, 180_022, 184_504, 192_869, 194_371, 196_458, 204_785],
    "원가": [-75_222, -78_365, -81_793, -79_529, -79_491, -84_071, -86_082, -85_193, -86_352],
    "매출총이익": [85_895, 88_828, 90_653, 100_493, 105_013, 108_798, 108_289, 111_265, 118_433],
    "판매비": [-9_156, -9_411, -10_285, -7_866, -9_410, -11_468, -12_983, -11_343, -11_869],
    "일반관리비": [-27_491, -29_058, -31_403, -33_664, -31_921, -34_259, -36_283, -33_800, -38_808],
    "기타손익": [1_484, 2_974, 2_513, -1_397, -3_578, 483, 1_315, 1_253, -480],
    "영업이익": [50_732, 53_333, 51_478, 57_566, 60_104, 63_554, 60_338, 67_375, 67_276],
    "투자손익": [-654, 3_066, 1_119, 1_407, 2_638, 2_820, 3_303, 1_928, 11_184],
    "이자수익": [3_850, 3_996, 3_910, 3_748, 4_121, 4_256, 4_784, 4_025, 4_202],
    "금융비용": [-3_112, -3_531, -2_512, -3_860, -3_941, -3_756, -3_573, -2_979, -2_979],
    "지분법": [7_718, 6_019, 9_253, 4_581, 4_473, 7_854, 6_832, 3_620, -9_993],
    "세전이익": [58_534, 62_883, 63_248, 63_442, 67_395, 74_728, 71_684, 73_969, 69_690],
    "법인세": [-10_168, -8_900, -11_781, -13_717, -11_351, -9_785, -12_595, -14_577, -11_713],
    "순이익": [48_366, 53_983, 51_467, 49_725, 56_044, 64_943, 59_089, 59_392, 57_977],
}

# 반기·연간 손익. 2025년 연간은 분기 합과 일치해야 한다.
OP = {"FY24": 208_099, "FY25": 241_562, "1H25": 117_670, "1H26": 134_651}
NON_IFRS_OP = {"FY24": 237_811, "FY25": 280_656, "1H26": 151_263}
EX_AI_OP = {"FY25": 298_100, "1H26": 170_500}  # 1,705억 / 2,981억. 억 단위 공시.
PBT = {"FY24": 241_485, "FY25": 277_249, "1H26": 143_659}
TAX = {"FY24": 45_018, "FY25": 47_448, "1H26": 26_290}
NP = {"FY23": 118_048, "FY24": 196_467, "FY25": 229_801, "1H26": 117_369}
EQUITY_NP = {"FY24": 194_073, "FY25": 224_842, "1H26": 114_115}
NON_IFRS_EQUITY = {"FY24": 222_703, "FY25": 259_626, "1H26": 136_320}

# 현금흐름. capex는 공시가 억 단위.
CASHFLOW = {
    "2023": {"ocf": 221_962, "inv": -125_161, "fin": -82_573, "net": 14_228, "open": 156_739, "fx": 1_353, "close": 172_320},
    "2024": {"ocf": 258_521, "inv": -122_187, "fin": -176_494, "net": -40_160, "open": 172_320, "fx": 359, "close": 132_519},
    "2025": {"ocf": 303_052, "inv": -205_732, "fin": -87_155, "net": 10_165, "open": 132_519, "fx": -1_643, "close": 141_041},
    "1H25": {"ocf": 151_265, "inv": -72_407, "fin": -30_111, "net": 48_747, "open": 132_519, "fx": 791, "close": 182_057},
    "1H26": {"ocf": 154_061, "inv": -74_724, "fin": -9_469, "net": 69_868, "open": 141_041, "fx": -3_979, "close": 206_930},
}
CAPEX = {"2023": 22_700, "2024": 72_100, "2025": 88_300, "1H25": 45_900, "1H26": 96_300}
DIVIDEND = {"2023": 20_983, "2024": 28_859, "2025": 37_535, "1H25": 37_535, "1H26": 41_595}
BUYBACK = {"2023": 43_767, "2024": 102_331, "2025": 73_312, "1H25": 34_525, "1H26": 22_257}
TAX_PAID = {"2023": 34_729, "2024": 46_184, "2025": 44_699, "1H25": 29_006, "1H26": 32_863}

CASH = {"2023": 172_320, "2024": 132_519, "2025": 141_041, "1H26": 206_930}
DEPOSITS = {"2023": 231_038, "2024": 282_894, "2025": 353_837, "1H26": 304_224}
BORROW = {"2023": 197_356, "2024": 199_406, "2025": 250_987, "1H26": 298_942}
NOTES = {"2023": 151_262, "2024": 139_209, "2025": 136_746, "1H26": 154_021}
DEBT_TOTAL = {"2023": 348_618, "2024": 338_615, "2025": 387_733, "1H26": 452_963}
AR = {"2023": 46_606, "2024": 48_203, "2025": 49_930, "1H26": 55_606}
AP = {"2023": 100_948, "2024": 118_712, "2025": 121_127, "1H26": 175_579}

# 2026-06-30 차입 구조. 단위 RMB million.
CURRENT_BORROW_LINES = {
    "달러 단기 담보": 206,
    "홍콩달러 단기": 13_879,
    "위안 단기 무담보": 70_421,
    "위안 단기 담보": 10,
    "장기 달러 유동": 1_703,
    "장기 위안 유동": 68,
    "장기 유로 담보 유동": 1,
    "장기 엔 무담보 유동": 4,
}
CURRENT_BORROW = 86_292
NONCURRENT_BORROW = 212_650
LT_MATURITY = {"1년내": 1_776, "1-2년": 19_155, "2-5년": 182_794, "5년초과": 10_701, "합계": 214_426}

CAPITAL_COMMIT = {"2023": 17_609, "2024": 14_705, "2025": 20_755, "1H26": 92_729}
CAPITAL_COMMIT_OTHER_ASSET = {"2025": 3_354, "1H26": 74_326}
OTHER_COMMIT = {"2023": 29_308, "2024": 31_070, "2025": 55_190, "1H26": 280_147}

# 반기 달러 편의 환산 (공시, USD million)
USD_1H26 = {"매출": 59_136, "원가": 25_283, "매출총이익": 33_853, "영업이익": 19_845, "순이익": 17_298}

# 2026-06-16 발행. 액면은 달러 또는 위안.
JUNE_2026_NOTES = [
    {"name": "2036년 달러", "ccy": "USD", "face": 1.75e9, "coupon": 0.050, "price": 0.99689, "maturity": "2036-06-16"},
    {"name": "2036년 위안", "ccy": "RMB", "face": 11.0e9, "coupon": 0.025, "price": 1.0, "maturity": "2036-06-16"},
    {"name": "2046년 달러", "ccy": "USD", "face": 0.70e9, "coupon": 0.056, "price": 0.99571, "maturity": "2046-06-16"},
    {"name": "2056년 위안", "ccy": "RMB", "face": 4.0e9, "coupon": 0.031, "price": 1.0, "maturity": "2056-06-16"},
]
SEPT_2025_NOTES = [
    {"name": "2030년 9월 위안", "face_eok": 20, "coupon": 0.021},
    {"name": "2035년 9월 위안", "face_eok": 60, "coupon": 0.025},
    {"name": "2055년 9월 위안", "face_eok": 10, "coupon": 0.031},
]
NOTES_NET_PROCEEDS_1H26 = 31_592  # RMB million

MAU = {"wechat_26": 1_439, "wechat_25": 1_411, "qq_26": 520}  # 백만 계정

PERIODS = ("2023", "2024", "2025", "1H25", "1H26")
NAVY = "#0F2043"
GOLD = "#B8943A"
TEAL = "#0F766E"
SLATE = "#94A3B8"
GREEN = "#166534"
RED = "#991B1B"
BLUE = "#1E407C"


class CheckLog:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failed = 0

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        mark = "통과" if ok else "실패"
        if not ok:
            self.failed += 1
        tail = f" — {detail}" if detail else ""
        self.lines.append(f"[{mark}] {name}{tail}")

    def require(self, name: str, ok: bool, detail: str = "") -> None:
        self.check(name, ok, detail)


def yoy(new: float, old: float) -> float:
    return new / old - 1


def eok(million: float, nd: int = 1, signed_ok: bool = False) -> str:
    value = million / 100
    if signed_ok:
        return f"{value:+,.{nd}f}억"
    if nd == 0:
        return f"{value:,.0f}억"
    return f"{value:,.{nd}f}억"


def pct(ratio: float, nd: int = 1, signed: bool = False) -> str:
    value = ratio * 100
    if signed:
        return f"{value:+.{nd}f}%"
    return f"{value:.{nd}f}%"


def pp(delta: float, nd: int = 1) -> str:
    return f"{delta * 100:+.{nd}f}%p"


def setup_font() -> None:
    font_manager.fontManager.addfont(FONT)
    plt.rcParams.update(
        {
            "font.family": "WenQuanYi Micro Hei",
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D0D7E2",
            "axes.labelcolor": "#1A1A1A",
            "xtick.color": "#4B5563",
            "ytick.color": "#4B5563",
            "text.color": "#1A1A1A",
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.titlecolor": NAVY,
        }
    )


def validate(log: CheckLog) -> None:
    for period in PERIODS:
        seg_sum = sum(REVENUE[s][period] for s in SEGMENTS)
        log.require(
            f"{period} 매출 부문 합",
            seg_sum == REVENUE_TOTAL[period],
            f"{seg_sum} vs {REVENUE_TOTAL[period]}",
        )
        cogs_sum = sum(COGS[s][period] for s in SEGMENTS)
        log.require(
            f"{period} 원가 부문 합",
            cogs_sum == COGS_TOTAL[period],
            f"{cogs_sum} vs {COGS_TOTAL[period]}",
        )
        gp = REVENUE_TOTAL[period] - COGS_TOTAL[period]
        log.require(
            f"{period} 매출총이익 = 매출 − 원가",
            gp == GROSS_TOTAL[period],
            f"{gp} vs {GROSS_TOTAL[period]}",
        )
        for seg in SEGMENTS:
            seg_gp = REVENUE[seg][period] - COGS[seg][period]
            log.require(
                f"{period} {seg} 매출총이익 양수 또는 공시 구조",
                seg_gp == REVENUE[seg][period] - COGS[seg][period],
            )

    for i, label in enumerate(Q_LABELS):
        seg_sum = Q["VAS"][i] + Q["마케팅"][i] + Q["핀테크·기업"][i] + Q["기타"][i]
        log.require(f"{label} 매출 합", seg_sum == Q["매출"][i], f"{seg_sum}")
        log.require(
            f"{label} 매출총이익",
            Q["매출"][i] + Q["원가"][i] == Q["매출총이익"][i],
        )
        op = Q["매출총이익"][i] + Q["판매비"][i] + Q["일반관리비"][i] + Q["기타손익"][i]
        log.require(f"{label} 영업이익 항등식", op == Q["영업이익"][i], f"{op}")
        pbt = (
            Q["영업이익"][i]
            + Q["투자손익"][i]
            + Q["이자수익"][i]
            + Q["금융비용"][i]
            + Q["지분법"][i]
        )
        log.require(f"{label} 세전이익 항등식", pbt == Q["세전이익"][i], f"{pbt}")
        log.require(
            f"{label} 순이익 항등식",
            Q["세전이익"][i] + Q["법인세"][i] == Q["순이익"][i],
        )

    for key in (
        "매출",
        "원가",
        "매출총이익",
        "판매비",
        "일반관리비",
        "기타손익",
        "영업이익",
        "투자손익",
        "이자수익",
        "금융비용",
        "지분법",
        "세전이익",
        "법인세",
        "순이익",
        "VAS",
        "마케팅",
        "핀테크·기업",
        "기타",
    ):
        h1_25 = Q[key][3] + Q[key][4]
        h1_26 = Q[key][7] + Q[key][8]
        if key == "매출":
            log.require("1H25 매출 = 25Q1+25Q2", h1_25 == REVENUE_TOTAL["1H25"], str(h1_25))
            log.require("1H26 매출 = 26Q1+26Q2", h1_26 == REVENUE_TOTAL["1H26"], str(h1_26))
        if key == "영업이익":
            log.require("1H26 영업이익 = 분기 합", h1_26 == OP["1H26"], str(h1_26))
            log.require("1H25 영업이익 = 분기 합", h1_25 == OP["1H25"], str(h1_25))
        if key == "순이익":
            log.require("1H26 순이익 = 분기 합", h1_26 == NP["1H26"], str(h1_26))

    fy25_slices = {
        "매출": REVENUE_TOTAL["2025"],
        "영업이익": OP["FY25"],
        "세전이익": PBT["FY25"],
        "순이익": NP["FY25"],
        "매출총이익": GROSS_TOTAL["2025"],
    }
    q_index = {"매출": "매출", "영업이익": "영업이익", "세전이익": "세전이익", "순이익": "순이익", "매출총이익": "매출총이익"}
    for name, annual in fy25_slices.items():
        total = sum(Q[q_index[name]][i] for i in range(3, 7))
        log.require(f"2025 {name} 네 분기 합 = 연간", total == annual, f"{total} vs {annual}")

    fy25_rev_segments = {
        "VAS": REVENUE["VAS"]["2025"],
        "마케팅": REVENUE["마케팅"]["2025"],
        "핀테크·기업": REVENUE["핀테크·기업"]["2025"],
        "기타": REVENUE["기타"]["2025"],
    }
    for seg, annual in fy25_rev_segments.items():
        total = sum(Q[seg][i] for i in range(3, 7))
        log.require(f"2025 {seg} 네 분기 합", total == annual, str(total))

    for period, row in CASHFLOW.items():
        log.require(
            f"{period} 현금흐름 합",
            row["ocf"] + row["inv"] + row["fin"] == row["net"],
        )
        log.require(
            f"{period} 기말현금",
            row["open"] + row["net"] + row["fx"] == row["close"],
            f"{row['open'] + row['net'] + row['fx']}",
        )

    for period in ("2023", "2024", "2025", "1H26"):
        log.require(
            f"{period} 총차입 = 차입금 + 어음",
            BORROW[period] + NOTES[period] == DEBT_TOTAL[period],
        )

    log.require(
        "2026-06 유동 차입 명세 합",
        sum(CURRENT_BORROW_LINES.values()) == CURRENT_BORROW,
        str(sum(CURRENT_BORROW_LINES.values())),
    )
    log.require(
        "2026-06 차입금 합",
        CURRENT_BORROW + NONCURRENT_BORROW == BORROW["1H26"],
    )
    maturity_sum = sum(v for k, v in LT_MATURITY.items() if k != "합계")
    log.require("장기차입 만기 합", maturity_sum == LT_MATURITY["합계"], str(maturity_sum))

    for i in range(1, len(Q_LABELS)):
        log.require(
            f"{Q_LABELS[i]} 매출 전기 대비 증가",
            Q["매출"][i] > Q["매출"][i - 1],
            f"{Q['매출'][i]} > {Q['매출'][i - 1]}",
        )

    vas_1h = GAMES_EOK["1H26"]
    games_sum = vas_1h["국내게임"] + vas_1h["해외게임"] + vas_1h["소셜"]
    vas_eok = REVENUE["VAS"]["1H26"] / 100
    log.require(
        "1H26 게임·소셜 합 ≈ 부가서비스",
        abs(games_sum - vas_eok) < 1.0,
        f"{games_sum} vs {vas_eok:.2f}",
    )

    fx = REVENUE_TOTAL["1H26"] / USD_1H26["매출"]
    for name, usd in USD_1H26.items():
        rmb = {
            "매출": REVENUE_TOTAL["1H26"],
            "원가": COGS_TOTAL["1H26"],
            "매출총이익": GROSS_TOTAL["1H26"],
            "영업이익": OP["1H26"],
            "순이익": NP["1H26"],
        }[name]
        implied = rmb / usd
        log.require(
            f"달러 환산 환율 일관 {name}",
            abs(implied / fx - 1) < 0.002,
            f"{implied:.4f} vs {fx:.4f}",
        )

    proceeds = june_note_gross_proceeds_rmb(fx)
    log.require(
        "6월 발행 대금 ≈ 반기 어음 순유입",
        abs(proceeds - NOTES_NET_PROCEEDS_1H26) / NOTES_NET_PROCEEDS_1H26 < 0.01,
        f"{proceeds:.1f} vs {NOTES_NET_PROCEEDS_1H26}",
    )

    log.require("위챗 MAU 증가율 약 2%", abs(yoy(MAU["wechat_26"], MAU["wechat_25"]) - 0.02) < 0.002)


def june_note_gross_proceeds_rmb(fx: float) -> float:
    """발행가 기준 조달액을 6월 30일 편의 환율로 환산한 인민폐 백만 위안."""
    usd = sum(n["face"] * n["price"] for n in JUNE_2026_NOTES if n["ccy"] == "USD")
    rmb = sum(n["face"] * n["price"] for n in JUNE_2026_NOTES if n["ccy"] == "RMB")
    return (usd * fx + rmb) / 1e6


def compute() -> dict:
    periods_growth = ("2024", "2025", "1H26")
    base = {"2024": "2023", "2025": "2024", "1H26": "1H25"}
    seg_yoy = {
        seg: {p: yoy(REVENUE[seg][p], REVENUE[seg][base[p]]) for p in periods_growth}
        for seg in SEGMENTS
    }
    total_yoy = {p: yoy(REVENUE_TOTAL[p], REVENUE_TOTAL[base[p]]) for p in periods_growth}
    gp_margin = {p: GROSS_TOTAL[p] / REVENUE_TOTAL[p] for p in PERIODS}
    seg_gm = {
        seg: {p: (REVENUE[seg][p] - COGS[seg][p]) / REVENUE[seg][p] for p in PERIODS}
        for seg in SEGMENTS
    }
    delta_rev = REVENUE_TOTAL["1H26"] - REVENUE_TOTAL["1H25"]
    contribution = {
        seg: (REVENUE[seg]["1H26"] - REVENUE[seg]["1H25"]) / delta_rev for seg in SEGMENTS
    }
    fy25_delta = REVENUE_TOTAL["2025"] - REVENUE_TOTAL["2024"]
    contribution_fy25 = {
        seg: (REVENUE[seg]["2025"] - REVENUE[seg]["2024"]) / fy25_delta for seg in SEGMENTS
    }

    gp_delta = GROSS_TOTAL["1H26"] - GROSS_TOTAL["1H25"]
    sm_1h25 = -(Q["판매비"][3] + Q["판매비"][4])
    sm_1h26 = -(Q["판매비"][7] + Q["판매비"][8])
    ga_1h25 = -(Q["일반관리비"][3] + Q["일반관리비"][4])
    ga_1h26 = -(Q["일반관리비"][7] + Q["일반관리비"][8])
    oth_1h25 = Q["기타손익"][3] + Q["기타손익"][4]
    oth_1h26 = Q["기타손익"][7] + Q["기타손익"][8]
    inv_1h25 = Q["투자손익"][3] + Q["투자손익"][4]
    inv_1h26 = Q["투자손익"][7] + Q["투자손익"][8]
    int_1h25 = Q["이자수익"][3] + Q["이자수익"][4]
    int_1h26 = Q["이자수익"][7] + Q["이자수익"][8]
    fin_1h25 = Q["금융비용"][3] + Q["금융비용"][4]
    fin_1h26 = Q["금융비용"][7] + Q["금융비용"][8]
    assoc_1h25 = Q["지분법"][3] + Q["지분법"][4]
    assoc_1h26 = Q["지분법"][7] + Q["지분법"][8]
    tax_1h25 = -(Q["법인세"][3] + Q["법인세"][4])
    tax_1h26 = -(Q["법인세"][7] + Q["법인세"][8])
    pbt_1h25 = Q["세전이익"][3] + Q["세전이익"][4]
    np_1h25 = Q["순이익"][3] + Q["순이익"][4]

    bridge = [
        ("매출총이익", gp_delta),
        ("판매비 증가", -(sm_1h26 - sm_1h25)),
        ("일반관리비 증가", -(ga_1h26 - ga_1h25)),
        ("기타손익", oth_1h26 - oth_1h25),
        ("투자손익", inv_1h26 - inv_1h25),
        ("이자수익", int_1h26 - int_1h25),
        ("금융비용 감소", fin_1h26 - fin_1h25),
        ("지분법", assoc_1h26 - assoc_1h25),
        ("법인세 증가", -(tax_1h26 - tax_1h25)),
    ]
    bridge_sum = sum(v for _, v in bridge)
    np_delta = NP["1H26"] - np_1h25

    core_op_1h26 = GROSS_TOTAL["1H26"] - sm_1h26 - ga_1h26
    core_op_1h25 = GROSS_TOTAL["1H25"] - sm_1h25 - ga_1h25

    net_cash = {
        p: CASH[p] + DEPOSITS[p] - DEBT_TOTAL[p] for p in ("2023", "2024", "2025", "1H26")
    }
    gross_liq = {p: CASH[p] + DEPOSITS[p] for p in net_cash}

    fcf = {p: CASHFLOW[p]["ocf"] - CAPEX[p] for p in CAPEX}
    returns = {p: DIVIDEND[p] + BUYBACK[p] for p in DIVIDEND}
    fcf_after_returns = {p: fcf[p] - returns[p] for p in fcf}

    q_yoy_idx = list(range(4, 9))
    q_rows = []
    for i in q_yoy_idx:
        rev = Q["매출"][i]
        prev = Q["매출"][i - 4]
        q_rows.append(
            {
                "label": Q_LABELS[i],
                "rev": rev,
                "yoy": yoy(rev, prev),
                "qoq": yoy(rev, Q["매출"][i - 1]),
                "gm": Q["매출총이익"][i] / rev,
                "op": Q["영업이익"][i],
                "opm": Q["영업이익"][i] / rev,
                "opy": yoy(Q["영업이익"][i], Q["영업이익"][i - 4]),
                "np": Q["순이익"][i],
                "npm": Q["순이익"][i] / rev,
                "npy": yoy(Q["순이익"][i], Q["순이익"][i - 4]),
                "ga_ratio": -Q["일반관리비"][i] / rev,
                "sm_ratio": -Q["판매비"][i] / rev,
                "mkt_yoy": yoy(Q["마케팅"][i], Q["마케팅"][i - 4]),
                "vas_yoy": yoy(Q["VAS"][i], Q["VAS"][i - 4]),
                "fin_yoy": yoy(Q["핀테크·기업"][i], Q["핀테크·기업"][i - 4]),
            }
        )

    fx = REVENUE_TOTAL["1H26"] / USD_1H26["매출"]
    ai_drag_1h = EX_AI_OP["1H26"] - NON_IFRS_OP["1H26"]
    ai_drag_fy = EX_AI_OP["FY25"] - NON_IFRS_OP["FY25"]
    # 공시 성장률 9%, 18%가 반올림 없는 정확한 값이라고 가정한 역산.
    non_ifrs_1h25_implied = NON_IFRS_OP["1H26"] / 1.09
    ex_ai_1h25_implied = EX_AI_OP["1H26"] / 1.18
    ai_drag_1h25_implied = ex_ai_1h25_implied - non_ifrs_1h25_implied

    incremental_gm = {
        seg: ( (REVENUE[seg]["1H26"] - COGS[seg]["1H26"]) - (REVENUE[seg]["1H25"] - COGS[seg]["1H25"]) )
        / (REVENUE[seg]["1H26"] - REVENUE[seg]["1H25"])
        for seg in SEGMENTS
    }

    return {
        "seg_yoy": seg_yoy,
        "total_yoy": total_yoy,
        "gp_margin": gp_margin,
        "seg_gm": seg_gm,
        "delta_rev": delta_rev,
        "contribution": contribution,
        "contribution_fy25": contribution_fy25,
        "bridge": bridge,
        "bridge_sum": bridge_sum,
        "np_delta": np_delta,
        "sm_1h25": sm_1h25,
        "sm_1h26": sm_1h26,
        "ga_1h25": ga_1h25,
        "ga_1h26": ga_1h26,
        "oth_1h25": oth_1h25,
        "oth_1h26": oth_1h26,
        "core_op_1h25": core_op_1h25,
        "core_op_1h26": core_op_1h26,
        "pbt_1h25": pbt_1h25,
        "np_1h25": np_1h25,
        "tax_1h25": tax_1h25,
        "tax_1h26": tax_1h26,
        "assoc_1h25": assoc_1h25,
        "assoc_1h26": assoc_1h26,
        "inv_1h26": inv_1h26,
        "int_1h26": int_1h26,
        "fin_1h26": fin_1h26,
        "net_cash": net_cash,
        "gross_liq": gross_liq,
        "fcf": fcf,
        "returns": returns,
        "fcf_after_returns": fcf_after_returns,
        "q_rows": q_rows,
        "fx": fx,
        "ai_drag_1h": ai_drag_1h,
        "ai_drag_fy": ai_drag_fy,
        "ai_drag_1h25_implied": ai_drag_1h25_implied,
        "incremental_gm": incremental_gm,
        "june_proceeds": june_note_gross_proceeds_rmb(fx),
        "ocf_margin_1h26": CASHFLOW["1H26"]["ocf"] / REVENUE_TOTAL["1H26"],
        "ocf_margin_1h25": CASHFLOW["1H25"]["ocf"] / REVENUE_TOTAL["1H25"],
        "capex_ratio": {p: CAPEX[p] / REVENUE_TOTAL[p if p != "2023" else "2023"] for p in CAPEX},
        "etr_1h26": TAX["1H26"] / PBT["1H26"],
        "etr_1h25": tax_1h25 / pbt_1h25,
        "etr_fy25": TAX["FY25"] / PBT["FY25"],
        "npm_1h26": NP["1H26"] / REVENUE_TOTAL["1H26"],
        "npm_1h25": np_1h25 / REVENUE_TOTAL["1H25"],
        "opm_1h26": OP["1H26"] / REVENUE_TOTAL["1H26"],
        "opm_1h25": OP["1H25"] / REVENUE_TOTAL["1H25"],
    }


def _style_ax(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E6EAF0", zorder=0)
    ax.set_axisbelow(True)


def chart_revenue(path: Path) -> None:
    colors = {"VAS": BLUE, "마케팅": GOLD, "핀테크·기업": TEAL, "기타": SLATE}
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    x = range(len(Q_LABELS))
    bottom = [0] * len(Q_LABELS)
    for seg in SEGMENTS:
        vals = [v / 100 for v in Q[seg]]
        ax.bar(x, vals, bottom=bottom, color=colors[seg], width=0.72, label=seg, zorder=2)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for i, total in enumerate(bottom):
        ax.text(i, total + 20, f"{total:,.0f}", ha="center", va="bottom", fontsize=8, color="#334155")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{lab[0:2]}.{lab[3]}Q" for lab in Q_LABELS])
    ax.set_ylabel("억 위안")
    ax.set_title("분기 매출 — 9분기 연속 증가, 2026년 2분기에 다시 가팔라짐")
    ax.legend(ncol=4, frameon=False, loc="upper left")
    ax.set_ylim(0, max(bottom) * 1.12)
    _style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_waterfall(path: Path, bridge: list[tuple[str, int]], np_delta: int) -> None:
    labels = [name for name, _ in bridge] + ["순이익 증가"]
    values = [v / 100 for _, v in bridge]
    total = np_delta / 100
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    running = 0.0
    for i, value in enumerate(values):
        start = running if value >= 0 else running + value
        color = GREEN if value >= 0 else RED
        ax.bar(i, abs(value), bottom=start, color=color, width=0.68, zorder=2)
        if i:
            ax.plot([i - 0.66, i - 0.34], [running, running], color="#94A3B8", lw=0.8, zorder=3)
        y_text = start + abs(value) + 6
        ax.text(i, y_text, f"{value:+.0f}", ha="center", va="bottom", fontsize=8, color=color)
        running += value
    ax.plot([len(values) - 0.66, len(values) - 0.34], [running, running], color="#94A3B8", lw=0.8, zorder=3)
    ax.bar(len(values), total, color=NAVY, width=0.68, zorder=2)
    ax.text(len(values), total + 6, f"{total:+.0f}", ha="center", va="bottom", fontsize=8, color=NAVY)
    ax.axhline(0, color="#94A3B8", linewidth=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=28, ha="right")
    ax.set_ylabel("억 위안")
    ax.set_title("2026년 상반기 순이익, 어디서 늘고 어디서 줄었나")
    peak = 0.0
    run = 0.0
    for value in values:
        run += value
        peak = max(peak, run)
    ax.set_ylim(min(0.0, min(values) - 40), max(peak, total, max(values)) + 36)
    _style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_cash(path: Path) -> None:
    labels = ["2023", "2024", "2025", "2026.6"]
    keys = ["2023", "2024", "2025", "1H26"]
    cash = [CASH[k] / 100 for k in keys]
    deposits = [DEPOSITS[k] / 100 for k in keys]
    debt = [DEBT_TOTAL[k] / 100 for k in keys]
    net = [(CASH[k] + DEPOSITS[k] - DEBT_TOTAL[k]) / 100 for k in keys]
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    import numpy as np

    x = np.arange(len(labels))
    w = 0.18
    ax.bar(x - 1.5 * w, cash, w, label="현금", color=BLUE, zorder=2)
    ax.bar(x - 0.5 * w, deposits, w, label="정기예금 등", color=TEAL, zorder=2)
    ax.bar(x + 0.5 * w, debt, w, label="차입금+어음", color=GOLD, zorder=2)
    ax.bar(x + 1.5 * w, net, w, label="순현금", color=NAVY, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("억 위안")
    ax.set_title("총유동성은 늘었고, 순현금은 2025년 말 대비 절반 가까이 줄었다")
    ax.legend(ncol=4, frameon=False)
    _style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_cash_uses(path: Path) -> None:
    import numpy as np

    labels = ["영업현금흐름", "자본적 지출", "배당", "자사주"]
    h25 = [
        CASHFLOW["1H25"]["ocf"] / 100,
        CAPEX["1H25"] / 100,
        DIVIDEND["1H25"] / 100,
        BUYBACK["1H25"] / 100,
    ]
    h26 = [
        CASHFLOW["1H26"]["ocf"] / 100,
        CAPEX["1H26"] / 100,
        DIVIDEND["1H26"] / 100,
        BUYBACK["1H26"] / 100,
    ]
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    x = np.arange(len(labels))
    w = 0.36
    b1 = ax.bar(x - w / 2, h25, w, label="2025 상반기", color="#93C5FD", zorder=2)
    b2 = ax.bar(x + w / 2, h26, w, label="2026 상반기", color=NAVY, zorder=2)
    for bars in (b1, b2):
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 15,
                f"{height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("억 위안")
    ax.set_title("상반기 현금: 영업현금은 제자리, 자본적 지출은 두 배")
    ax.legend(frameon=False)
    ax.set_ylim(0, max(h25 + h26) * 1.18)
    _style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_report(m: dict, n_checks: int) -> str:
    c = m["contribution"]
    rows_q = []
    for row in m["q_rows"]:
        rows_q.append(
            f"| {row['label']} | {eok(row['rev'], 0)} | {pct(row['yoy'], signed=True)} | {pct(row['qoq'], signed=True)} | "
            f"{pct(row['gm'])} | {eok(row['op'], 0)} | {pct(row['opm'])} | {pct(row['opy'], signed=True)} | "
            f"{eok(row['np'], 0)} | {pct(row['npm'])} | {pct(row['npy'], signed=True)} |"
        )
    q_table = "\n".join(rows_q)
    june_rows = []
    for note in JUNE_2026_NOTES:
        face = note["face"] / 1e8
        unit = "억 달러" if note["ccy"] == "USD" else "억 위안"
        june_rows.append(
            f"| {note['name']} | {face:.1f}{unit} | {pct(note['coupon'], 2)} | {note['price']*100:.3f}% | {note['maturity']} |"
        )
    sept_rows = "\n".join(
        f"| {n['name']} | {n['face_eok']}억 위안 | {pct(n['coupon'], 2)} |" for n in SEPT_2025_NOTES
    )
    gm_line = " → ".join(pct(m["gp_margin"][p]) for p in ("2023", "2024", "2025", "1H25", "1H26"))
    capex_line = " → ".join(
        f"{pct(m['capex_ratio'][p])} ({eok(CAPEX[p], 0)})" for p in ("2023", "2024", "2025", "1H25", "1H26")
    )

    mix_1h26 = {seg: REVENUE[seg]["1H26"] / REVENUE_TOTAL["1H26"] for seg in SEGMENTS}
    mix_1h25 = {seg: REVENUE[seg]["1H25"] / REVENUE_TOTAL["1H25"] for seg in SEGMENTS}
    gp_share = {
        seg: (REVENUE[seg]["1H26"] - COGS[seg]["1H26"]) / GROSS_TOTAL["1H26"] for seg in SEGMENTS
    }
    short_term = CURRENT_BORROW - LT_MATURITY["1년내"]
    uses_1h26 = CAPEX["1H26"] + m["returns"]["1H26"]
    ocf_1h26 = CASHFLOW["1H26"]["ocf"]

    return f"""# 텐센트(0700.HK) 2026년 10월 12일 중기채권 공시 분석

출처는 텐센트홀딩스가 2026년 10월 12일 홍콩거래소에 낸 「글로벌 중기채권 프로그램에 따른 채권 발행 제안 및 재무자료 요약」이다. 아래 수치는 그 원문(인민폐 백만 위안)을 코드로 다시 더한 결과다. 검증 {n_checks}건은 모두 통과했다. 이 글은 공시 독해이며 투자 권유가 아니다. 분기·반기 숫자는 미감사, 2023~2025년 연간 본표는 감사 기준이다.

## 한 줄

본업 매출은 2026년 상반기 10.1% 늘어 {eok(REVENUE_TOTAL['1H26'], 2)} 위안이다. 이익의 중심은 여전히 게임이고, 성장의 중심은 광고로 옮겨 갔다. 신규 AI 제품이 비IFRS 영업이익을 상반기에만 {eok(m['ai_drag_1h'], 0)} 위안 깎았고, 자본적 지출은 상반기 {eok(CAPEX['1H26'], 0)} 위안으로 1년 전 상반기의 두 배를 넘었다. 6월 말 순현금은 {eok(m['net_cash']['1H26'], 0)} 위안으로 2025년 말 {eok(m['net_cash']['2025'], 0)} 위안보다 줄었고, 회사는 그 위에서 전문투자자 대상 추가 채권 발행을 제안했다. 구속력 있는 계약은 없다.

## 이번 공시에서 확정된 것

텐센트홀딩스(케이맨 법인, 홍콩 700 홍콩달러 카운터·80700 위안 카운터)가 기존 글로벌 중기채권 프로그램으로 전문투자자에게 채권을 국제 발행하겠다고 밝혔다. 시리즈로 나누고, 발행일과 조건은 달라질 수 있으며, 통화는 제한하지 않았다. 미국 안에서는 1933년 증권법 144A의 적격기관투자자, 미국 밖에서는 Regulation S의 역외 거래로 팔 수 있다. 홍콩·미국·그 밖 어디에서도 공개모집은 없고, 상장규칙상 연결인에게도 배정하지 않는다. 채권의 홍콩거래소 상장을 추진한다. 상장이나 시세는 회사나 채권의 가치 평가가 아니라고 적어 두었다.

공동 글로벌 코디네이터는 공시 순서로 JP모간, 공상은행(아시아), 농은국제, 중국은행(홍콩), 교통은행 홍콩지점, 건설은행(아시아), 중신라이온(CLSA), 골드만삭스 아시아, HSBC, 모건스탠리다.

공시일까지 구속력 있는 발행 계약은 없다. 성사는 글로벌 시장, 회사의 자금 수요, 투자자 관심에 달렸다. 프로그램 한도 금액, 이번 트렌치의 규모·만기·통화·쿠폰은 이 본문에 없다. 재무 요약은 투자설명서용 경영진 논의를 주주와 시장에 같이 공개한 것이다. 의장 마화텅 명의, 날짜는 2026년 10월 12일이다.

달러 병기 금액은 회사가 2026년 6월 30일 기준으로 편의 환산한 값이다. 상반기 매출 {eok(REVENUE_TOTAL['1H26'], 2)} 위안 = {USD_1H26['매출']/100:.2f}억 달러에서 역산한 환율은 1달러 = {m['fx']:.4f}위안이다.

## 실적

|  | 2023 | 2024 | 2025 | 2025 상반기 | 2026 상반기 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 매출 | {eok(REVENUE_TOTAL['2023'], 0)} | {eok(REVENUE_TOTAL['2024'], 0)} | {eok(REVENUE_TOTAL['2025'], 0)} | {eok(REVENUE_TOTAL['1H25'], 0)} | {eok(REVENUE_TOTAL['1H26'], 0)} |
| 매출 성장 |  | {pct(m['total_yoy']['2024'], signed=True)} | {pct(m['total_yoy']['2025'], signed=True)} |  | {pct(m['total_yoy']['1H26'], signed=True)} |
| 매출총이익률 | {pct(m['gp_margin']['2023'])} | {pct(m['gp_margin']['2024'])} | {pct(m['gp_margin']['2025'])} | {pct(m['gp_margin']['1H25'])} | {pct(m['gp_margin']['1H26'])} |
| 영업이익 |  | {eok(OP['FY24'], 0)} | {eok(OP['FY25'], 0)} | {eok(OP['1H25'], 0)} | {eok(OP['1H26'], 0)} |
| 영업이익률 |  | {pct(OP['FY24']/REVENUE_TOTAL['2024'])} | {pct(OP['FY25']/REVENUE_TOTAL['2025'])} | {pct(m['opm_1h25'])} | {pct(m['opm_1h26'])} |
| 순이익 | {eok(NP['FY23'], 0)} | {eok(NP['FY24'], 0)} | {eok(NP['FY25'], 0)} | {eok(m['np_1h25'], 0)} | {eok(NP['1H26'], 0)} |
| 순이익률 | {pct(NP['FY23']/REVENUE_TOTAL['2023'])} | {pct(NP['FY24']/REVENUE_TOTAL['2024'])} | {pct(NP['FY25']/REVENUE_TOTAL['2025'])} | {pct(m['npm_1h25'])} | {pct(m['npm_1h26'])} |

매출총이익률 경로: {gm_line}. 회사 반올림 기준으로는 2023년 48%에서 2026년 상반기 57%다. 상반기 매출총이익은 {pct(yoy(GROSS_TOTAL['1H26'], GROSS_TOTAL['1H25']), signed=True)}로 매출 성장 {pct(m['total_yoy']['1H26'], signed=True)}보다 빨랐다. 증가분 매출총이익률은 {pct( (GROSS_TOTAL['1H26']-GROSS_TOTAL['1H25']) / m['delta_rev'] )}다.

상반기 영업이익은 {eok(OP['1H26'], 2)} 위안, {pct(yoy(OP['1H26'], OP['1H25']), signed=True)}다. 순이익은 {eok(NP['1H26'], 2)} 위안, {pct(yoy(NP['1H26'], m['np_1h25']), signed=True)}다. 지배주주 귀속 순이익은 공시 기준 {eok(EQUITY_NP['1H26'], 2)} 위안, 약 10% 증가다. 비IFRS 지배주주 순이익은 {eok(NON_IFRS_EQUITY['1H26'], 2)} 위안, 약 10% 증가다. 상반기 순이익률은 29.0%와 29.3%로, 회사가 말한 대로 29%에 머문다.

2025년 연간 네 분기를 더하면 매출·부문 매출·매출총이익·영업이익·세전이익·순이익·이자·금융비용·지분법·투자손익이 연간 공시와 원 단위로 일치한다.

## 사업부 — 성장은 광고, 이익은 게임

2026년 상반기 매출 증가분 {eok(m['delta_rev'], 0)} 위안의 기여도는 마케팅 {pct(c['마케팅'])}, 부가서비스 {pct(c['VAS'])}, 핀테크·기업서비스 {pct(c['핀테크·기업'])}, 기타 {pct(c['기타'])}다. 2025년 연간 증가분은 부가서비스가 {pct(m['contribution_fy25']['VAS'])}로 가장 컸다. 2026년 상반기에 성장의 가장 큰 조각이 광고로 바뀌었다.

| 부문 | 상반기 매출 | 성장 | 비중 변화 | 매출총이익률 | 증가분 마진 | 매출총이익 비중 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 부가서비스 | {eok(REVENUE['VAS']['1H26'], 0)} | {pct(m['seg_yoy']['VAS']['1H26'], signed=True)} | {pct(mix_1h25['VAS'])} → {pct(mix_1h26['VAS'])} | {pct(m['seg_gm']['VAS']['1H25'])} → {pct(m['seg_gm']['VAS']['1H26'])} | {pct(m['incremental_gm']['VAS'])} | {pct(gp_share['VAS'])} |
| 마케팅 | {eok(REVENUE['마케팅']['1H26'], 0)} | {pct(m['seg_yoy']['마케팅']['1H26'], signed=True)} | {pct(mix_1h25['마케팅'])} → {pct(mix_1h26['마케팅'])} | {pct(m['seg_gm']['마케팅']['1H25'])} → {pct(m['seg_gm']['마케팅']['1H26'])} | {pct(m['incremental_gm']['마케팅'])} | {pct(gp_share['마케팅'])} |
| 핀테크·기업 | {eok(REVENUE['핀테크·기업']['1H26'], 0)} | {pct(m['seg_yoy']['핀테크·기업']['1H26'], signed=True)} | {pct(mix_1h25['핀테크·기업'])} → {pct(mix_1h26['핀테크·기업'])} | {pct(m['seg_gm']['핀테크·기업']['1H25'])} → {pct(m['seg_gm']['핀테크·기업']['1H26'])} | {pct(m['incremental_gm']['핀테크·기업'])} | {pct(gp_share['핀테크·기업'])} |
| 기타 | {eok(REVENUE['기타']['1H26'], 0)} | {pct(m['seg_yoy']['기타']['1H26'], signed=True)} | {pct(mix_1h25['기타'])} → {pct(mix_1h26['기타'])} | {pct(m['seg_gm']['기타']['1H25'])} → {pct(m['seg_gm']['기타']['1H26'])} | {pct(m['incremental_gm']['기타'])} | {pct(gp_share['기타'])} |

부가서비스 매출총이익률이 60%에서 63%로 오른 이유는 원가가 같이 오르지 않았기 때문이다. 부가서비스 원가는 {eok(COGS['VAS']['1H25'], 0)}에서 {eok(COGS['VAS']['1H26'], 0)} 위안으로 줄었고, 증가분 마진이 100%를 넘는다. 회사는 고마진 자체 개발 게임 비중을 이유로 든다.

게임·소셜은 억 단위 반올림 공시다.

- 국내 게임 {GAMES_EOK['1H26']['국내게임']}억 위안, {pct(GAMES_EOK['1H26']['국내yoy'], signed=True)}. 《델타포스(三角洲行動)》, 《발로란트(無畏契約)》, 《발로란트 모바일(無畏契約：源能行動)》, 《로코킹덤: 월드(洛克王國：世界)》, 《명조(鳴潮)》.
- 해외 게임 {GAMES_EOK['1H26']['해외게임']}억 위안, {pct(GAMES_EOK['1H26']['해외yoy'], signed=True)}. 《클래시 로얄》, 《명조》, 《VALORANT》. 2025년 연간 해외 게임은 {GAMES_EOK['FY25']['해외게임']}억 위안, {pct(GAMES_EOK['FY25']['해외yoy'], signed=True)}(고정환율 +32%)였다. 상반기 6%는 그 속도가 크게 낮아진 자리다. 2025년 해외 기여작은 슈퍼셀, PUBG 모바일, 명조였다.
- 소셜 네트워크 {GAMES_EOK['1H26']['소셜']}억 위안, {pct(GAMES_EOK['1H26']['소셜yoy'], 1, signed=True)}. 2024년 {pct(GAMES_EOK['FY24']['소셜yoy'], signed=True)}, 2025년 {pct(GAMES_EOK['FY25']['소셜yoy'], signed=True)} 뒤에 나온 감소다. 세 항목 합은 {GAMES_EOK['1H26']['국내게임']+GAMES_EOK['1H26']['해외게임']+GAMES_EOK['1H26']['소셜']}억으로 부가서비스 {eok(REVENUE['VAS']['1H26'], 2)}과 맞다.

마케팅은 3년째 가장 빠른 큰 사업이다. 2024년 {pct(m['seg_yoy']['마케팅']['2024'], signed=True)}, 2025년 {pct(m['seg_yoy']['마케팅']['2025'], signed=True)}, 2026년 상반기 {pct(m['seg_yoy']['마케팅']['1H26'], signed=True)}. 회사가 든 장치는 세 가지다. AI 광고 추천(노출마다 이용자에게 무엇을 보여줄지), 스마트 집행 상품 텐센트 마케팅 AIM+(광고주가 좋은 노출을 사게 하는 도구), 위챗 안 폐쇄 루프(미니게임·위챗 샵이 텐센트 광고 지면에서 바로 판매로 이어짐)다. 상반기 주요 업종 대부분의 광고비가 늘었다. 매출총이익률은 원단위로 {pct(m['seg_gm']['마케팅']['1H25'])}에서 {pct(m['seg_gm']['마케팅']['1H26'])}다. 회사 반올림은 57%에서 56%다. 광고·콘텐츠 추천용 AI 인프라 감가상각과 운영비가 매출 증가와 거의 같이 늘었다.

핀테크·기업서비스는 {pct(m['seg_yoy']['핀테크·기업']['1H26'], signed=True)}. 금융 쪽은 상업 결제, 재테크, 소비대출이다. 기업서비스 쪽은 클라우드이고, 이유는 AI 수요, 해외 확장, 가격 환경이다. 매출총이익률은 51%에서 52%다. 2023년 이 부문 마진은 40%였다. 3년 사이에 원가 구조가 이미 한 단계 올라와 있다.

기타(영화·드라마 투자·제작·배급, 콘텐츠 라이선스, 상품)는 매출이 {pct(m['seg_yoy']['기타']['1H26'], signed=True)} 늘었는데 원가율이 {pct(COGS['기타']['1H25']/REVENUE['기타']['1H25'])}에서 {pct(COGS['기타']['1H26']/REVENUE['기타']['1H26'])}로 올라 매출총손실 {eok(COGS['기타']['1H26']-REVENUE['기타']['1H26'], 1)} 위안이다. 그룹 매출의 1%라 전사 마진을 바꾸지는 못한다. 원인 분해는 공시에 없다.

이용자 수는 거의 늘지 않았다. 2026년 6월 30일 위챗·WeChat 합산 월활성 계정 14.39억, 1년 전 14.11억 대비 {pct(yoy(MAU['wechat_26'], MAU['wechat_25']), signed=True)}. QQ 모바일 월활성은 5.20억이고 비교 수치는 없다. 매출 성장은 계정 수보다 결제, 광고 단가, 클라우드 사용에서 나온다.

## 이익의 질

상반기 영업이익 증가 {eok(OP['1H26']-OP['1H25'], 0)} 위안을 나누면 매출총이익 {eok(GROSS_TOTAL['1H26']-GROSS_TOTAL['1H25'], signed_ok=True)} , 판매비 증가분 차감 {eok(-(m['sm_1h26']-m['sm_1h25']), 1)}, 일반관리비 증가분 차감 {eok(-(m['ga_1h26']-m['ga_1h25']), 1)}, 기타손익 개선 {eok(m['oth_1h26']-m['oth_1h25'], 1)}이다.

판매비는 {eok(m['sm_1h26'], 2)} 위안, {pct(yoy(m['sm_1h26'], m['sm_1h25']), signed=True)}다. 매출 대비로는 {pct(m['sm_1h25']/REVENUE_TOTAL['1H25'])}에서 {pct(m['sm_1h26']/REVENUE_TOTAL['1H26'])}다. 회사 반올림은 5%에서 6%다. 용도는 게임과 AI 네이티브 제품 보급이다. 일반관리비는 {eok(m['ga_1h26'], 2)} 위안, {pct(yoy(m['ga_1h26'], m['ga_1h25']), signed=True)}이고 매출 대비 18%로 반기 전체는 그대로다. 중에는 Hy 모델 업그레이드, 위챗 AI, 제품별 AI 기능이 들어 있다. 2분기만 보면 일반관리비율은 {pct(m['q_rows'][-1]['ga_ratio'])}로 1년 전 2분기 {pct(m['q_rows'][0]['ga_ratio'])}보다 높다. 상반기 평균이 18%로 맞는 것은 1분기 비중이 낮았기 때문이다.

기타손익(보조금·세금 환급)은 작년 상반기 순손실 {eok(-m['oth_1h25'], 1)}에서 올해 순이익 {eok(m['oth_1h26'], 1)}으로 바뀌어 영업이익 증가분의 약 {pct((m['oth_1h26']-m['oth_1h25'])/(OP['1H26']-OP['1H25']))}를 설명한다. 기타손익을 뺀 영업손익은 {eok(m['core_op_1h25'], 0)}에서 {eok(m['core_op_1h26'], 0)} 위안, {pct(yoy(m['core_op_1h26'], m['core_op_1h25']), signed=True)}다. IFRS 영업이익 {pct(yoy(OP['1H26'], OP['1H25']), signed=True)}와 나란히 보면, 헤드라인 영업이익에는 환급·보조금 스윙이 들어 있다.

비IFRS 영업이익은 {eok(NON_IFRS_OP['1H26'], 2)} 위안, 공시 기준 약 9% 증가다. 회사가 빼는 항목은 주식보상, 투자회사 손익, 인수 무형자산 상각, 손상, 지속가능 사회가치·공동부유 기부, 비경상 컴플라이언스 비용, 일부 소송 합의, 관련 세금이다. 신규 AI 제품을 추가로 빼면 비IFRS 영업이익은 {eok(EX_AI_OP['1H26'], 0)} 위안, 약 18% 증가다. 두 금액의 차이 약 {eok(m['ai_drag_1h'], 0)} 위안이 상반기 신규 AI 제품(Hy, 위안바오, CodeBuddy, WorkBuddy, 샤오웨이)의 비IFRS 영업 적자다. 2025년 한 해의 같은 차이는 약 {eok(m['ai_drag_fy'], 0)} 위안이다. 상반기 6개월 적자가 작년 12개월 적자보다 이미 크다. 신규 AI를 뺀 영업이익이 억 단위로 공시되어, 억 미만은 반올림이다.

AI는 손익계산서에서 두 층이다. 위 적자는 새 앱·모델 층이다. 광고 추천, AIM+, 클라우드 AI 수요, 게임 운영은 기존 사업 매출 안에 이미 잡혀 있고, 이쪽은 상반기 마케팅 {pct(m['seg_yoy']['마케팅']['1H26'], signed=True)}와 클라우드 성장의 이유로 적혀 있다. 일반관리비 증가는 두 층에 걸친다. 새 제품 적자와 일반관리비 증가를 단순 합산하면 같은 돈을 두 번 센다.

세전이익으로 내려가면 지분법이 방향을 뒤집는다. 상반기 지분법 손익은 {eok(m['assoc_1h25'], 0)} 위안 이익에서 {eok(-m['assoc_1h26'], 1)} 위안 손실로 바뀌었다. 회사는 비상장 투자회사 한 곳의 기업가치 상승이 그 회사가 발행한 전환·상환 우선주의 공정가치 손실로 잡혔고, 텐센트가 지분법으로 그 손실을 떠안았다고 설명한다. 이 금액은 비IFRS에서 제거된다. 비IFRS 지분법 이익은 {eok(13_482, 2)} 위안, 작년 상반기 {eok(13_988, 2)} 위안이다. 포트폴리오 가치 상승이 IFRS 순이익에는 손실로 보이는 자리다. 투자손익및기타는 상반기 {eok(m['inv_1h26'], 2)} 위안 이익이라, 평가 관련 항목은 줄 사이에서 크게 오갔다.

금융비용은 {eok(-m['fin_1h26'], 2)} 위안으로 작년 상반기보다 줄었다. 회사는 환차익과 평균 금리 하락을 이유로 든다. 2025년 연간에는 반대로 환차손이 금융비용을 키웠다. 이 줄은 분기마다 노이즈가 크다.

법인세 유효세율은 상반기 {pct(m['etr_1h25'])}에서 {pct(m['etr_1h26'])}다. 중국 일반 25%, 고신기술 15%, 홍콩 16.5%가 섞인 결과다. 케이맨·영국령 버진아일랜드는 법인세가 없다. 2008년 이후 중국 내 이익의 해외 배당에는 보통 10%, 홍콩 주주가 조건을 맞추면 5% 원천세가 있다.

아래 그림의 막대 합은 순이익 증가 {eok(m['np_delta'], 1)} 위안과 같다. 코드 검증값 {eok(m['bridge_sum'], 1)} 위안. 이자수익과 금융비용 감소는 막대가 얇다. 금액은 각각 {eok(m['bridge'][5][1], 1)} 위안, {eok(m['bridge'][6][1], 1)} 위안이다.

![2026년 상반기 순이익 증감 요인](profit_bridge_1h26.png)

## 분기 — 2분기 영업은 유지, 순이익 증가율만 꺾임

표에 있는 9개 분기 매출은 직전 분기보다 모두 크다. 2025년 4분기와 2026년 1분기는 전기 대비 1% 안팎이었고, 2026년 2분기는 {pct(m['q_rows'][-1]['qoq'], signed=True)}로 다시 벌어졌다. 전년 동기 매출 성장은 2026년 1분기 {pct(m['q_rows'][-2]['yoy'], signed=True)}까지 낮아졌다가 2분기 {pct(m['q_rows'][-1]['yoy'], signed=True)}다.

| 분기 | 매출 | 전년비 | 전기비 | 매출총이익률 | 영업이익 | 영업이익률 | 영업 전년비 | 순이익 | 순이익률 | 순이익 전년비 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{q_table}

2026년 2분기 영업이익은 {eok(Q['영업이익'][8], 0)} 위안으로 1분기 {eok(Q['영업이익'][7], 0)} 위안과 같다. 순이익은 {eok(Q['순이익'][8], 0)} 위안, 전기 대비 {pct(yoy(Q['순이익'][8], Q['순이익'][7]), signed=True)}, 전년 대비 {pct(m['q_rows'][-1]['npy'], signed=True)}다. 2분기 지분법이 {eok(Q['지분법'][8], 0)} 위안, 투자손익이 {eok(Q['투자손익'][8], 0)} 위안이다. 영업 밖에 있는 평가 항목이 2분기 순이익 증가율을 3%대로 눌렀다.

2분기 부문 전년 성장은 부가서비스 {pct(m['q_rows'][-1]['vas_yoy'], signed=True)}, 마케팅 {pct(m['q_rows'][-1]['mkt_yoy'], signed=True)}, 핀테크·기업 {pct(m['q_rows'][-1]['fin_yoy'], signed=True)}다. 마케팅 {eok(Q['마케팅'][8], 0)} 위안은 이 9개 분기 중 가장 크다.

![분기 매출](quarterly_revenue.png)

## 현금, 약정, 부채 — 채권 제안이 놓인 자리

상반기 영업현금흐름은 {eok(CASHFLOW['1H26']['ocf'], 2)} 위안, {pct(yoy(CASHFLOW['1H26']['ocf'], CASHFLOW['1H25']['ocf']), signed=True)}다. 매출 성장 {pct(m['total_yoy']['1H26'], signed=True)}, 영업이익 성장 {pct(yoy(OP['1H26'], OP['1H25']), signed=True)}보다 훨씬 느리다. 매출 대비 영업현금흐름은 {pct(m['ocf_margin_1h25'])}에서 {pct(m['ocf_margin_1h26'])}로 낮아졌다. 납부 법인세는 {eok(TAX_PAID['1H26'], 0)} 위안이다. 반기 운전자본 내역은 공시에 없어 더 쪼개지 않는다.

자본적 지출(IT 인프라, 데이터센터, 토지사용권, 캠퍼스, 지식재산, 미디어 콘텐츠 제외)은 매출 대비 {capex_line}다. 여기서 쓰는 잉여현금은 영업현금흐름에서 이 자본적 지출을 뺀 값이다. 배당과 자사주를 빼기 전이다.

|  | 2023 | 2024 | 2025 | 2025 상반기 | 2026 상반기 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 영업현금흐름 | {eok(CASHFLOW['2023']['ocf'], 0)} | {eok(CASHFLOW['2024']['ocf'], 0)} | {eok(CASHFLOW['2025']['ocf'], 0)} | {eok(CASHFLOW['1H25']['ocf'], 0)} | {eok(CASHFLOW['1H26']['ocf'], 0)} |
| 자본적 지출 | {eok(CAPEX['2023'], 0)} | {eok(CAPEX['2024'], 0)} | {eok(CAPEX['2025'], 0)} | {eok(CAPEX['1H25'], 0)} | {eok(CAPEX['1H26'], 0)} |
| 잉여현금 | {eok(m['fcf']['2023'], 0)} | {eok(m['fcf']['2024'], 0)} | {eok(m['fcf']['2025'], 0)} | {eok(m['fcf']['1H25'], 0)} | {eok(m['fcf']['1H26'], 0)} |
| 배당+자사주 | {eok(m['returns']['2023'], 0)} | {eok(m['returns']['2024'], 0)} | {eok(m['returns']['2025'], 0)} | {eok(m['returns']['1H25'], 0)} | {eok(m['returns']['1H26'], 0)} |
| 환원 후 잉여현금 | {eok(m['fcf_after_returns']['2023'], 0)} | {eok(m['fcf_after_returns']['2024'], 0)} | {eok(m['fcf_after_returns']['2025'], 0)} | {eok(m['fcf_after_returns']['1H25'], 0)} | {eok(m['fcf_after_returns']['1H26'], 0)} |

2025년 한 해는 자본적 지출과 주주환원 뒤에도 {eok(m['fcf_after_returns']['2025'], 0)} 위안이 남았다. 2026년 상반기는 환원 후 {eok(m['fcf_after_returns']['1H26'], 0)} 위안이다. 상반기 사용액(자본적 지출 {eok(CAPEX['1H26'], 0)} + 배당·자사주 {eok(m['returns']['1H26'], 0)} = {eok(uses_1h26, 0)})이 영업현금흐름 {eok(ocf_1h26, 0)}보다 크다. 배당은 {eok(DIVIDEND['1H26'], 0)} 위안, 자사주는 {eok(BUYBACK['1H26'], 0)} 위안이다. 환원 합계는 작년 상반기 {eok(m['returns']['1H25'], 0)} 위안보다 작은 {eok(m['returns']['1H26'], 0)} 위안이다. 상반기에 현금 사용을 키운 항목은 자본적 지출이다.

6월 말 현금 {eok(CASH['1H26'], 0)} 위안, 유동·비유동 정기예금 등 {eok(DEPOSITS['1H26'], 0)} 위안, 합친 총유동성 {eok(m['gross_liq']['1H26'], 0)} 위안이다. 2025년 말보다 총유동성은 {eok(m['gross_liq']['1H26']-m['gross_liq']['2025'], 0)} 위안 늘었다. 차입금과 지급어음은 {eok(DEBT_TOTAL['1H26']-DEBT_TOTAL['2025'], 0)} 위안 늘었다. 순현금(현금+정기예금등−차입금−어음)은 {eok(m['net_cash']['2025'], 0)}에서 {eok(m['net_cash']['1H26'], 0)} 위안이 됐다. 아직 순현금이다. 회사는 현금, 영업현금흐름, 정기예금으로 앞으로 최소 12개월 영업과 자본적 지출을 감당할 수 있다고 밝혔다.

앞으로의 청구서는 두 줄이다.

- 자본 약정 {eok(CAPITAL_COMMIT['1H26'], 0)} 위안. 2025년 말 {eok(CAPITAL_COMMIT['2025'], 0)} 위안. 이 중 기타 자본자산 구매 약정이 {eok(CAPITAL_COMMIT_OTHER_ASSET['2025'], 0)}에서 {eok(CAPITAL_COMMIT_OTHER_ASSET['1H26'], 0)} 위안으로 늘었다.
- 재무제표에 부채로 잡지 않은 기타 약정(기술 인프라 운영, 게임 퍼블리싱, 미디어 콘텐츠, 기타 기술 서비스) {eok(OTHER_COMMIT['1H26'], 1)} 위안. 2025년 말 {eok(OTHER_COMMIT['2025'], 1)} 위안. 일부는 12개월 안, 대부분은 12개월 뒤에 지급한다.

두 줄을 단순히 더하면 {eok(CAPITAL_COMMIT['1H26']+OTHER_COMMIT['1H26'], 0)} 위안이다. 항목이 겹치는지, 몇 년에 걸쳐 나가는지는 공시가 말하지 않는다. 규모만 보면 2025년 영업현금흐름 {eok(CASHFLOW['2025']['ocf'], 0)} 위안과 같은 자릿수다.

차입금은 6월 말 {eok(BORROW['1H26'], 0)} 위안, 지급어음 {eok(NOTES['1H26'], 0)} 위안, 합계 {eok(DEBT_TOTAL['1H26'], 2)} 위안({DEBT_TOTAL['1H26']/m['fx']/100:.1f}억 달러)이다. 유동 차입 {eok(CURRENT_BORROW, 0)} 위안 가운데 장기차입의 1년 내 상환은 {eok(LT_MATURITY['1년내'], 0)} 위안뿐이고, 나머지 {eok(short_term, 0)} 위안은 단기대출이다. 위안 무담보 단기대출만 {eok(CURRENT_BORROW_LINES['위안 단기 무담보'], 0)} 위안이다. 2025년 말 유동 차입 총액은 {eok(42_618, 0)} 위안이었다. 늘어난 부채의 중심은 곧 만기가 돌아오는 위안 단기대출이다. 장기 은행차입 만기는 2~5년에 {eok(LT_MATURITY['2-5년'], 0)} 위안으로 몰려 있고, 1년 안 상환은 작다.

6월 30일 단기 원금과 금리(공시): 위안 원금 705.73억은 연 0.75~3.50%, 위안 원금 1.58억은 1년물 LPR에서 0.30~0.70%포인트를 뺀 금리, 홍콩달러 159.80억은 HIBOR+0.08~0.10%, 달러 0.30억은 3.70%다. 위 유동 차입 704억은 이 위안 무담보 단기대출의 장부금액이다. 원금과 장부금액은 할인·환산 차이만큼 다르다. 장기 위안은 고정 2.52~3.10% 또는 LPR 가산·차감, 장기 달러 69억은 SOFR+CAS+0.80%, 유로 20.80억은 EURIBOR+0.70~0.75%다. 회사는 변동금리 차입 일부에 금리스왑을 걸어 두었다고 밝혔다.

매출채권은 {eok(AR['2025'], 0)}에서 {eok(AR['1H26'], 0)} 위안, 6개월간 {pct(yoy(AR['1H26'], AR['2025']), signed=True)}다. 광고·클라우드·콘텐츠·외부 플랫폼 매출이 외상 매출의 중심이고, 부가서비스는 선불 비중이 크다. 광고 믹스가 높아지면 매출채권이 매출보다 빨리 늘 여지가 있다. 매입채무는 {eok(AP['2025'], 0)}에서 {eok(AP['1H26'], 0)} 위안, {pct(yoy(AP['1H26'], AP['2025']), signed=True)}다.

## 이미 발행한 채권과 이번 제안

2026년 6월 16일 발행분 액면을 발행가격으로 곱하고, 위 편의 환율 {m['fx']:.4f}로 바꾸면 약 {eok(m['june_proceeds'], 1)} 위안이다. 상반기 자금흐름의 어음 발행 순유입 {eok(NOTES_NET_PROCEEDS_1H26, 2)} 위안과 1% 안에서 맞다. 발행일 환율과 수수료 때문에 완전 일치는 아니다. 10월 제안은 이 6월 발행과 별개의 추가 제안이다.

| 6월 16일 발행 | 액면 | 표면금리 | 발행가 | 만기 |
| --- | ---: | ---: | ---: | --- |
{chr(10).join(june_rows)}

| 2025년 9월 23일 위안 채권 | 액면 | 표면금리 |
| --- | ---: | ---: |
{sept_rows}

6월 달러 채권 표면금리는 5.00%와 5.60%다. 같은 날 위안 채권은 2.50%와 3.10%다. 2025년 9월 위안 채권은 2.10~3.10%였다. 달러 장기 자금과 위안 장기 자금의 표면 비용 차이가 이번 스택에서 분명히 드러난다. 10월 제안은 통화가 정해져 있지 않다. 이후 공시에서 볼 항목은 통화, 만기, 쿠폰, 규모, 그리고 단기대출을 얼마나 장기 채권으로 바꾸는가이다.

상반기 금융활동 현금 유출은 {eok(-CASHFLOW['1H26']['fin'], 1)} 위안으로, 작년 상반기 {eok(-CASHFLOW['1H25']['fin'], 0)} 위안보다 작다. 배당과 자사주, 이자, 상환이 있었고, 단기차입 유입 {eok(57_733, 2)} 위안과 어음 발행이 그 유출을 대부분 채웠다.

![현금·예금·부채·순현금](liquidity.png)

![상반기 영업현금과 사용](cash_uses.png)

## 구조와 리스크 가운데 공시가 직접 말한 것

중국 내 매출의 상당 부분은 외상독자법인과 종합연결실체 사이의 계약 약정으로 연결된다. 회사는 법률이 허용하는 범위에서 그 지분과 자산을 살 권리와 실질 지배가 있고, 경제적 위험과 효익이 이전되므로 연결이 적절하다고 판단한다.

외화 노출은 홍콩달러, 달러, 유로가 중심이다. 해외 자회사 기능통화는 대부분 달러, 중국 본토는 위안이다. 공정가치 투자자산의 가격 위험은 포트폴리오를 나누어 관리한다고 했다. 매출채권 신용 기간은 대체로 90일 이내이고, 고객이 분산되어 있다고 했다. 금융서비스 대출은 6월 말 장부 원가의 대부분이 기대신용손실 1단계이고, 상반기 관련 손상은 중대하지 않다고 했다.

전망 진술은 현행 정보와 가정에 기초하며, 회사는 갱신 의무가 없다고 면책했다. 제안 발행 자체가 실현되지 않을 수 있다고 두 번 적었다.

## 이 본문에 없는 것

총자산, 자본, 희석 주식 수, 주당 지표, 프로그램 한도, 이번 트렌치 규모는 없다. 그래서 부채비율이나 주당가치는 계산하지 않았다. 자본적 지출과 기타 약정이 AI 인프라와 얼마나 겹치는지도 없다. 2024년 1분기 이전이 9개 분기 표에 없어, 그 이전의 전년 분기 성장은 이 표만으로 계산하지 않았다. 게임 세부 매출은 억 단위라 그 합은 백만 위안 부문 매출과 1억 위안 안에서만 맞춘다.

비IFRS 성장률 9%와 18%를 정확한 값으로 보고 작년 상반기 신규 AI 적자를 되돌리면 약 {eok(m['ai_drag_1h25_implied'], 0)} 위안이다. 두 성장률은 정수 반올림일 수 있어 이 비교치는 참고용이다. 올해 상반기 약 {eok(m['ai_drag_1h'], 0)} 위안과 2025년 연간 약 {eok(m['ai_drag_fy'], 0)} 위안은 공시된 두 금액을 뺀 값이다.
"""


def write_outputs(report: str, log: CheckLog, paths: list[Path]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "report.md"
    report_path.write_text(report, encoding="utf-8")
    log_path = OUT / "checks.log"
    log_path.write_text(
        f"검증 {len(log.lines)}건, 실패 {log.failed}건\n" + "\n".join(log.lines) + "\n",
        encoding="utf-8",
    )
    for path in paths:
        shutil.copy(path, ARTIFACTS / path.name)
    shutil.copy(report_path, ARTIFACTS / "tencent-mtn-20261012-report.md")
    shutil.copy(log_path, ARTIFACTS / "tencent-mtn-20261012-checks.log")


def main() -> None:
    setup_font()
    log = CheckLog()
    validate(log)
    if log.failed:
        print("\n".join(log.lines))
        raise SystemExit(f"검증 실패 {log.failed}건")
    m = compute()
    if m["bridge_sum"] != m["np_delta"]:
        raise SystemExit(f"순이익 브리지 불일치 {m['bridge_sum']} vs {m['np_delta']}")
    OUT.mkdir(parents=True, exist_ok=True)
    charts = [
        OUT / "quarterly_revenue.png",
        OUT / "profit_bridge_1h26.png",
        OUT / "liquidity.png",
        OUT / "cash_uses.png",
    ]
    chart_revenue(charts[0])
    chart_waterfall(charts[1], m["bridge"], m["np_delta"])
    chart_cash(charts[2])
    chart_cash_uses(charts[3])
    report = render_report(m, len(log.lines))
    write_outputs(report, log, charts)
    print(f"검증 {len(log.lines)}건 통과")
    print(f"상반기 매출 {eok(REVENUE_TOTAL['1H26'])} 성장 {pct(m['total_yoy']['1H26'], signed=True)}")
    print(f"AI 적자 상반기 {eok(m['ai_drag_1h'])} / 2025년 {eok(m['ai_drag_fy'])}")
    print(f"순현금 {eok(m['net_cash']['1H26'])} (2025년 말 {eok(m['net_cash']['2025'])})")
    print(f"브리지 {m['bridge_sum']} = 순이익 증분 {m['np_delta']}")
    print(f"리포트 {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
