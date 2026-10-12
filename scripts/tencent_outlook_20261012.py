#!/usr/bin/env python3
"""텐센트 2026-10-12 공시 이후의 의도, 자금 사용, 금리, 12개월 주가 시나리오.

주가는 단일 예측이 아니다. 공시 실적에 성장·AI 적자·배수를 곱한 범위다.
시세와 금리는 2026-10-12 공개 시세, 실적은 중기채권 공시와 2026년 중간보고서 EPS다.

실행: python3 scripts/tencent_outlook_20261012.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze_tencent_mtn_20261012 as filing  # noqa: E402

OUT = filing.OUT
ARTIFACTS = filing.ARTIFACTS
FONT = filing.FONT

# 2026-10-12 시장 스냅샷. 공시 숫자가 아니다.
PRICE_HKD = 428.0  # FT, 10월 12일 종가. 당일 범위 423.40–430.40.
HKD_PER_CNY_PARITY = 100 / 85.768  # CFETS 중간가, 100홍콩달러 = 85.768위안.
CNY_PER_HKD = 85.768 / 100
SHARES_MN = 9_011  # 10월 11일 전후 유통 주식 수 약 90.11억 주.
EPS_SHARES_1H26_MN = 9_029  # 중간보고서 상반기 가중평균.
EPS_BASIC_1H26 = 12.639  # 중간보고서, 위안.
US_10Y = 0.0524  # 10월 12일 미국 10년 약 5.24%.
CN_10Y = 0.0169  # 10월 12일 중국 10년 약 1.69%.
USD_10Y_COUPON = 0.050  # 2026-06-16 달러 2036 채권.
USD_20Y_COUPON = 0.056
NAVY = "#0F2043"
GOLD = "#B8943A"
TEAL = "#0F766E"
GREEN = "#166534"
RED = "#991B1B"

# 표면금리가 공시된 위안 채권. 단위는 인민폐 백만 위안.
RMB_NOTES = [
    ("2030-09", 2_000, 0.021),
    ("2035-09", 6_000, 0.025),
    ("2055-09", 1_000, 0.031),
    ("2036", 11_000, 0.025),
    ("2056", 4_000, 0.031),
]
# 은행 차입 원금 구간. LPR 연동분은 금리가 확정 숫자가 아니다.
RMB_LOAN_BANDS = [
    ("단기 고정구간", 70_573, 0.0075, 0.0350),
    ("장기 고정구간", 69_085, 0.0252, 0.0310),
]
RMB_FLOATING_PRINCIPAL = 65_621 + 5_800 + 158  # 1년·5년 LPR 및 단기 LPR 소액.


def eok(million: float, nd: int = 0) -> str:
    return f"{million / 100:,.{nd}f}억"


def pct(x: float, nd: int = 1, signed: bool = False) -> str:
    v = x * 100
    return f"{v:+.{nd}f}%" if signed else f"{v:.{nd}f}%"


def rmb_to_hkd(rmb: float) -> float:
    return rmb * HKD_PER_CNY_PARITY


def setup_font() -> None:
    font_manager.fontManager.addfont(FONT)
    plt.rcParams.update(
        {
            "font.family": "WenQuanYi Micro Hei",
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D0D7E2",
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.titlecolor": NAVY,
        }
    )


def style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#E6EAF0")
    ax.set_axisbelow(True)


def note_coupon() -> tuple[float, float]:
    principal = sum(p for _, p, _ in RMB_NOTES)
    interest = sum(p * c for _, p, c in RMB_NOTES)
    return principal, interest / principal


def loan_interest_range() -> tuple[float, float, float]:
    """고정 구간 원금의 연간 이자. 반환은 (원금, 하단 이자, 상단 이자), 백만 위안."""
    principal = 0.0
    low = 0.0
    high = 0.0
    for _, face, floor, cap in RMB_LOAN_BANDS:
        principal += face
        low += face * floor
        high += face * cap
    return principal, low, high


def build() -> dict:
    principal, coupon = note_coupon()
    loan_face, loan_low, loan_high = loan_interest_range()
    price_rmb = PRICE_HKD * CNY_PER_HKD
    equity_1h26 = filing.EQUITY_NP["1H26"]
    eps_check = equity_1h26 / EPS_SHARES_1H26_MN
    # 중간보고서: 2025년 상반기 기본 EPS 11.367위안, 가중평균 91.01억 주.
    equity_1h25 = 11.367 * 9_101
    ttm_equity = filing.EQUITY_NP["FY25"] - equity_1h25 + equity_1h26
    ttm_eps = ttm_equity / SHARES_MN
    pe_ifrs = price_rmb / ttm_eps

    non_ifrs_1h26 = filing.NON_IFRS_EQUITY["1H26"]
    # 회사가 상반기 비IFRS 지배주주 순이익 증가율을 10%로 적었다. 역산은 참고치.
    non_ifrs_1h25_implied = non_ifrs_1h26 / 1.10
    ttm_non_ifrs = filing.NON_IFRS_EQUITY["FY25"] - non_ifrs_1h25_implied + non_ifrs_1h26
    ttm_non_ifrs_eps = ttm_non_ifrs / SHARES_MN
    pe_non_ifrs = price_rmb / ttm_non_ifrs_eps

    ex_ai_fy25 = filing.EX_AI_OP["FY25"]
    # 2027년 비IFRS 지배주주 순이익. 단위 백만 위안.
    # 경로는 2025년 AI 제외 영업이익에서 출발해 적자를 빼고, 영업이익→순이익 비율을 곱한 뒤 2027년에 한 번 더 성장시킨다.
    paths = {
        "회수": {"ex_ai_g": 0.16, "drag": 25_000, "drop": 0.92, "fy27_g": 0.14, "multiple": 16.0},
        "유지": {"ex_ai_g": 0.12, "drag": 34_000, "drop": 0.90, "fy27_g": 0.09, "multiple": pe_non_ifrs},
        "부담": {"ex_ai_g": 0.06, "drag": 42_000, "drop": 0.86, "fy27_g": 0.02, "multiple": 9.5},
    }
    scenarios = {}
    for name, p in paths.items():
        op26 = ex_ai_fy25 * (1 + p["ex_ai_g"]) - p["drag"]
        eq26 = op26 * p["drop"]
        eq27 = eq26 * (1 + p["fy27_g"])
        eps27 = eq27 / SHARES_MN
        px_rmb = eps27 * p["multiple"]
        px_hkd = rmb_to_hkd(px_rmb)
        scenarios[name] = {
            **p,
            "op26": op26,
            "eq26": eq26,
            "eq27": eq27,
            "eps27": eps27,
            "px_rmb": px_rmb,
            "px_hkd": px_hkd,
            "upside": px_hkd / PRICE_HKD - 1,
        }

    multiples = [10.0, 12.5, 16.0]
    matrix = {}
    for name, sc in scenarios.items():
        matrix[name] = {m: rmb_to_hkd(sc["eps27"] * m) for m in multiples}

    capex_1h = filing.CAPEX["1H26"]
    capex_2h25 = filing.CAPEX["2025"] - filing.CAPEX["1H25"]
    capex_fy26_if_2h_repeats_2h25 = capex_1h + capex_2h25
    capex_fy26_if_2h_equals_1h = capex_1h * 2
    dep_5y = capex_fy26_if_2h_equals_1h / 5
    rmb_stack = principal + loan_face + RMB_FLOATING_PRINCIPAL
    # 같은 원금을 자사 달러 10년 쿠폰으로 빌릴 때와 위안 가중 쿠폰으로 빌릴 때의 차이.
    # 대출 원금에는 가중 쿠폰을 그대로 씌운 예시이다. 실제 대출 금리는 구간 안에 있다.
    saving_vs_own_usd = rmb_stack * (USD_10Y_COUPON - coupon)
    saving_vs_ust = rmb_stack * (US_10Y - coupon)
    fixed_mid_rate = (loan_low + loan_high) / 2 / loan_face
    fixed_saving_vs_ust = loan_face * US_10Y - (loan_low + loan_high) / 2

    uses = {
        "capex_1h": capex_1h,
        "dividend_1h": filing.DIVIDEND["1H26"],
        "buyback_1h": filing.BUYBACK["1H26"],
        "capex_fy26_soft": capex_fy26_if_2h_repeats_2h25,
        "capex_fy26_hot": capex_fy26_if_2h_equals_1h,
        "capex_2h25": capex_2h25,
        "dep_5y_hot": dep_5y,
        "other_commit": filing.OTHER_COMMIT["1H26"],
        "cap_commit": filing.CAPITAL_COMMIT["1H26"],
    }

    return {
        "price_rmb": price_rmb,
        "coupon": coupon,
        "note_principal": principal,
        "note_interest": principal * coupon,
        "loan_face": loan_face,
        "loan_low": loan_low,
        "loan_high": loan_high,
        "fixed_mid_rate": fixed_mid_rate,
        "fixed_saving_vs_ust": fixed_saving_vs_ust,
        "rmb_stack": rmb_stack,
        "saving_vs_own_usd": saving_vs_own_usd,
        "saving_vs_ust": saving_vs_ust,
        "eps_check": eps_check,
        "equity_1h25": equity_1h25,
        "ttm_equity": ttm_equity,
        "ttm_eps": ttm_eps,
        "pe_ifrs": pe_ifrs,
        "ttm_non_ifrs": ttm_non_ifrs,
        "ttm_non_ifrs_eps": ttm_non_ifrs_eps,
        "pe_non_ifrs": pe_non_ifrs,
        "scenarios": scenarios,
        "matrix": matrix,
        "multiples": multiples,
        "uses": uses,
        "mkt_cap_hkd": PRICE_HKD * SHARES_MN * 1_000_000,
        "mkt_cap_rmb": price_rmb * SHARES_MN,
    }


def check(m: dict) -> None:
    eps_gap = abs(m["eps_check"] - EPS_BASIC_1H26)
    if eps_gap > 0.01:
        raise SystemExit(f"EPS 불일치 {m['eps_check']} vs {EPS_BASIC_1H26}")
    principal, coupon = note_coupon()
    if abs(principal - 24_000) > 1:
        raise SystemExit("위안 채권 원금 합 오류")
    if not 0.025 < coupon < 0.027:
        raise SystemExit(f"가중 쿠폰 이상 {coupon}")
    growth = filing.EQUITY_NP["1H26"] / m["equity_1h25"] - 1
    if abs(growth - 0.103) > 0.005:
        raise SystemExit(f"상반기 지배주주 순이익 성장 {growth}")
    base = m["scenarios"]["유지"]
    if abs(base["px_hkd"] - rmb_to_hkd(base["eps27"] * base["multiple"])) > 0.1:
        raise SystemExit("기준 주가 항등식 실패")
    if m["uses"]["capex_1h"] <= filing.CAPEX["2025"]:
        raise SystemExit("상반기 캡엑스가 연간을 넘지 않음")


def chart_prices(path: Path, m: dict) -> None:
    labels = ["부담", "유지", "회수"]
    colors = {"부담": RED, "유지": NAVY, "회수": GREEN}
    vals = [m["scenarios"][k]["px_hkd"] for k in labels]
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    bars = ax.bar(labels, vals, color=[colors[k] for k in labels], width=0.62, zorder=2)
    ax.axhline(PRICE_HKD, color=GOLD, lw=1.4, label=f"10월 12일 종가 {PRICE_HKD:.0f}")
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + 12,
            f"{val:.0f}",
            ha="center",
            va="bottom",
            fontsize=12,
            color=NAVY,
        )
    ax.set_ylabel("홍콩달러")
    ax.set_title("12개월 시나리오 주가. 유지 경로만 오늘 배수를 그대로 쓴다")
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0, max(vals) * 1.18)
    style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_rates(path: Path, m: dict) -> None:
    labels = [
        "중국 국채 10년",
        "텐센트 위안 채권\n가중 표면금리",
        "위안 단기 대출\n구간 중간",
        "위안 장기 고정\n구간 중간",
        "미국 국채 10년",
        "텐센트 달러 10년",
        "텐센트 달러 20년",
    ]
    short_mid = (0.0075 + 0.0350) / 2
    long_mid = (0.0252 + 0.0310) / 2
    vals = [CN_10Y, m["coupon"], short_mid, long_mid, US_10Y, USD_10Y_COUPON, USD_20Y_COUPON]
    colors = [TEAL, TEAL, TEAL, TEAL, GOLD, GOLD, GOLD]
    fig, ax = plt.subplots(figsize=(11.2, 5.8))
    x = range(len(labels))
    bars = ax.bar(x, [v * 100 for v in vals], color=colors, width=0.72, zorder=2)
    for bar, val in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.12,
            f"{val * 100:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("%")
    ax.set_title("위안 조달 금리는 2%대, 달러 조달 금리는 5%대")
    ax.set_ylim(0, 7.2)
    style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render(m: dict) -> str:
    sc = m["scenarios"]
    u = m["uses"]
    base, bull, bear = sc["유지"], sc["회수"], sc["부담"]
    rows = []
    for name in ("회수", "유지", "부담"):
        cells = " | ".join(f"{m['matrix'][name][mult]:.0f}" for mult in m["multiples"])
        rows.append(
            f"| {name} | {eok(sc[name]['eq27'])} | {sc[name]['eps27']:.1f} | {cells} |"
        )
    matrix_header = " | ".join(f"{mult:.1f}배" for mult in m["multiples"])
    ai_drag_1h = filing.EX_AI_OP["1H26"] - filing.NON_IFRS_OP["1H26"]
    return f"""# 텐센트, 돈을 어디에 쓰고 어떤 회사가 되려 하는가

2026년 10월 12일 종가 홍콩달러 {PRICE_HKD:.0f}원, 당일 범위 423.40–430.40, 52주 범위 411–664. 위안 환산은 같은 날 CFETS 중간가(홍콩달러 1원 = {CNY_PER_HKD:.5f}위안)로 주당 {m['price_rmb']:.1f}위안이다. 주식 수는 약 {SHARES_MN/100:,.2f}억 주. 시가총액은 약 {m['mkt_cap_hkd']/1e12:.2f}조 홍콩달러, {m['mkt_cap_rmb']/1e6:,.2f}조 위안이다.

이 글의 주가 범위는 예측 모델의 출력이다. 공시가 2027년 이익을 보장하지 않고, 배수도 모델이 고른 값이다.

## 의도

숫자가 보여주는 우선순위는 한 줄이다. 게임·광고·결제에서 나오는 현금으로 AI 인프라를 먼저 사고, 배당은 유지하고, 자사주는 줄였다.

상반기 자본적 지출은 {eok(u['capex_1h'])} 위안으로 2025년 한 해 {eok(filing.CAPEX['2025'])} 위안을 이미 넘었다. 작년 상반기보다 지출은 {eok(u['capex_1h']-filing.CAPEX['1H25'])} 위안 늘었다. 자사주는 {eok(filing.BUYBACK['1H25'])}에서 {eok(u['buyback_1h'])} 위안으로 줄었고, 배당은 {eok(filing.DIVIDEND['1H25'])}에서 {eok(u['dividend_1h'])} 위안으로 늘었다. 주주환원 감소분보다 설비 투자 증가분이 크다. 차액은 단기대출과 예금으로 메웠다.

같이 늘어난 계약이 업의 방향을 말한다. 기타 자본자산 구매 약정은 34억에서 743억 위안, 재무제표에 부채로 잡지 않은 기술·콘텐츠 약정은 552억에서 2,802억 위안이다. 회사는 앞으로 수년의 컴퓨팅과 기술 인프라를 지금 가격과 지금 위안 금리로 잠그고 있다.

채권 제안의 역할은 그 투자 자금을 만기가 짧은 위안 대출에서 긴 채권으로 옮기는 데 가깝다. 6월 말 유동 차입 863억 위안 중 845억이 단기대출이고, 그중 위안 무담보가 704억이다. 회사는 아직 순현금 582억 위안이 있고, 12개월 영업과 자본적 지출은 기존 현금으로 가능하다고 적었다. 유상증자는 하지 않는다. 배수가 낮아진 가격에서 주식을 새로 팔지 않겠다는 선택이다.

AI는 두 층으로 밀고 있다. 광고 추천, AIM+, 클라우드, 게임은 이미 매출로 잡힌다. Hy, 위안바오, CodeBuddy, WorkBuddy, 샤오웨이는 상반기 비IFRS 영업이익을 약 {eok(ai_drag_1h)} 위안 깎는 적자 사업이다. 회사는 이 적자를 숨기지 않고, 빼면 영업이익 성장이 18%라는 방식으로 채권 투자자에게 설명했다. 모델과 앱을 직접 갖고, 위챗으로 배포하겠다는 쪽이다.

해외 게임은 2025년 +33%에서 상반기 +6%로 느려졌다. 국내 게임은 +11%, 소셜은 -0.7%다. 다음 성장의 무게는 해외 게임 흥행보다 위챗 광고와 국내 자체 게임에 실려 있다.

## 앞으로 돈이 가는 곳

이미 나간 상반기 현금과, 하반기를 작년 하반기처럼 가정한 자리다.

| 용도 | 금액 | 의미 |
| --- | ---: | --- |
| 상반기 자본적 지출 | {eok(u['capex_1h'])} | IT, 데이터센터, 캠퍼스, 지식재산. 미디어 콘텐츠는 제외 |
| 작년 하반기 자본적 지출 | {eok(u['capex_2h25'])} | 2025년 883억에서 상반기 459억을 뺀 값 |
| 2026년 지출, 하반기가 작년과 같으면 | {eok(u['capex_fy26_soft'])} | 2025년 대비 {pct(u['capex_fy26_soft']/filing.CAPEX['2025']-1, signed=True)} |
| 2026년 지출, 하반기도 상반기와 같으면 | {eok(u['capex_fy26_hot'])} | 5년 정액 상각이면 매년 약 {eok(u['dep_5y_hot'])} |
| 상반기 배당 | {eok(u['dividend_1h'])} | 2025년 연간 배당이 상반기에 지급된 패턴 |
| 상반기 자사주 | {eok(u['buyback_1h'])} | 2024년 연간 1,023억, 2025년 733억에서 축소 |
| 자본 약정 | {eok(u['cap_commit'])} | 이미 계약, 아직 현금 유출 전 |
| 기타 약정 | {eok(u['other_commit'], 0)} | 인프라 운영, 게임, 미디어, 기술 서비스. 대부분 12개월 이후 |

상각이 이자보다 크다. 뜨거운 캡엑스 경로를 5년 정액으로 나누면 연 {eok(u['dep_5y_hot'])} 위안이다. 위안 부채 전부를 달러 10년 쿠폰 대신 위안 채권 금리로 빌릴 때 아껴지는 이자는 연 {eok(m['saving_vs_own_usd'])} 위안이다. AI 투자의 손익은 금리보다 그 설비가 매출을 만드는지에서 갈린다.

신규 AI 제품 적자는 비용의 다른 줄이다. 상반기 약 {eok(ai_drag_1h)} 위안, 2025년 한 해 약 {eok(filing.EX_AI_OP['FY25']-filing.NON_IFRS_OP['FY25'])} 위안. 현금이 설비로 가고, 손익은 새 앱 적자와 감가상각으로 깎인다.

## 어떤 회사가 되는가

2023년 텐센트는 매출 대비 자본적 지출 3.7%, 매출총이익률 48%인 플랫폼이었다. 2026년 상반기는 지출 비중 24%, 매출총이익률 57%다. 본업 마진은 좋아졌고, 자산은 무거워졌다.

남아 있는 이익의 모양은 그대로다. 상반기 매출총이익의 54%가 부가서비스, 성장분의 38%가 마케팅이다. 핀테크·기업서비스는 매출의 30%이고 증가 속도는 한 자릿수다. 다음 모습은 위챗 트래픽으로 광고·클라우드·게임을 팔고, 그 위에 AI 설비를 얹는 회사다.

그래서 3년 뒤의 모습은 세 갈래다.

- 회수. 광고와 클라우드가 AI 설비 값을 벌고, 새 앱 적자가 줄어 플랫폼 마진이 남는다. 게임은 계속 이익의 중심이다.
- 유지. 본업은 고성장 없이 한 자릿수 후반으로 크고, AI 적자는 상반기 속도 근처에 머문다. 회사는 현금 창출원과 설비 투자 회사를 한 몸에 둔다.
- 부담. 설비 약정이 감가상각과 운영비로 먼저 오고 매출은 늦게 온다. 이익은 거의 늘지 않고, 시장은 인터넷 회사 배수 대신 설비 회사 배수를 적용한다.

위챗 월활성 14.39억, 증가율 2%는 이용자 회사의 성장이 끝났다는 뜻이기도 하고, 그 이용자를 더 비싸게 파는 회사로 바뀌었다는 뜻이기도 하다. 광고 단가, 폐쇄 루프 거래, 클라우드 사용량이 계정 수를 대신한다.

## 미국보다 낮은 대출 금리

10월 12일 미국 10년 국채는 약 {pct(US_10Y, 2)}, 중국 10년 국채는 약 {pct(CN_10Y, 2)}다. 차이는 {pct(US_10Y-CN_10Y, 2)}포인트다.

텐센트의 위안 채권 가중 표면금리는 {pct(m['coupon'], 2)}다. 원금 {eok(m['note_principal'])} 위안, 연 이자 약 {eok(m['note_interest'], 1)} 위안. 6월에 직접 발행한 달러 10년은 {pct(USD_10Y_COUPON, 2)}, 달러 20년은 {pct(USD_20Y_COUPON, 2)}다. 싼 돈은 위안 부채다. 달러 부채는 미국 금리 구간에 있다. 홍콩달러 은행 차입은 HIBOR에 0.08~0.60%포인트를 더하므로 달러 금리에 가깝다.

![조달 금리 비교](funding_rates.png)

위안 은행 차입 중 금리가 구간으로 적힌 원금은 {eok(m['loan_face'])} 위안이다. 구간 끝으로 연 이자를 계산하면 {eok(m['loan_low'], 1)}에서 {eok(m['loan_high'], 1)} 위안이다. 중간 금리는 {pct(m['fixed_mid_rate'], 2)}다. LPR에 연동된 원금 약 {eok(RMB_FLOATING_PRINCIPAL)} 위안은 10월 12일 LPR이 이 공시에 없어 이자 금액을 확정하지 않았다.

예시로, 위안 채권·고정구간 대출·LPR 원금을 합친 {eok(m['rmb_stack'])} 위안 전부를 위안 채권 가중 금리 {pct(m['coupon'], 2)}로 빌리고, 같은 돈을 자사 달러 10년 쿠폰 {pct(USD_10Y_COUPON, 2)}로 빌리면 이자는 매년 {eok(m['saving_vs_own_usd'])} 위안 차이 난다. 미국 10년 국채 {pct(US_10Y, 2)}와 비교하면 차이는 {eok(m['saving_vs_ust'])} 위안이다. 국채 금리는 텐센트가 실제로 빌릴 수 있는 금리가 아니다. 비교 기준은 회사가 6월에 낸 달러 채권이다.

이 차이는 2025년 지배주주 순이익 {eok(filing.EQUITY_NP['FY25'])} 위안의 약 {pct(m['saving_vs_own_usd']/filing.EQUITY_NP['FY25'])}다. 상반기 AI 적자를 연간으로 그대로 두면 약 {eok(ai_drag_1h*2)} 위안인데, 금리 차이는 그 적자의 일부만 메운다. 장점은 맞다. 장점이 되는 자리는 한정되어 있다.

- 위안으로 버는 국내 설비에는 통화가 맞다. 데이터센터와 서버를 위안 부채로 사면 이자와 매출의 통화가 같다.
- 10년 위안 2.50%는 단기 위안 0.75~3.50%보다 언제나 싸지 않다. 이번 채권의 이득은 금리 그 자체보다 845억 단기대출의 차환 위험 축소다.
- 10월 제안이 달러로 나오면 이 장점은 그 회차에는 쓰이지 않는다. 6월 달러 채권은 이미 5.00%와 5.60%였다.
- 같은 금리 차이가 주식 배수에는 반대로 작용한다. 미국 무위험 수익률이 5.2%이면 홍콩 주식은 그보다 높은 이익 수익률을 줘야 한다. 오늘 주가의 최근 12개월 IFRS 이익 배수는 {m['pe_ifrs']:.1f}배, 이익 수익률 {pct(1/m['pe_ifrs'])}다. 비IFRS는 {m['pe_non_ifrs']:.1f}배, 이익 수익률 {pct(1/m['pe_non_ifrs'])}다. 싼 위안 부채가 회사 이자를 줄이는 동안, 높은 미국 금리는 외국인 주주가 요구하는 수익률을 높여 배수를 눌러 둔다.

52주 고가 664홍콩달러에서 428홍콩달러까지 가격은 약 {pct(PRICE_HKD/664-1)}다. 같은 기간 이익은 늘었다. 가격 하락의 중심은 배수 하락이다.

## 지금 주가의 위치

중간보고서 상반기 기본 주당순이익은 {EPS_BASIC_1H26:.3f}위안이다. 공시 지배주주 순이익 {eok(filing.EQUITY_NP['1H26'], 2)} 위안을 가중평균 {EPS_SHARES_1H26_MN/100:.2f}억 주로 나누면 {m['eps_check']:.3f}위안이라 중간보고서와 맞다. 작년 상반기 11.367위안, 가중평균 91.01억 주로 되돌리면 지배주주 순이익은 {eok(m['equity_1h25'], 1)} 위안, 증가율은 {pct(filing.EQUITY_NP['1H26']/m['equity_1h25']-1)}다. 회사가 말한 약 10%와 같다.

최근 12개월 IFRS 지배주주 순이익은 2025년 연간에서 작년 상반기를 빼고 올해 상반기를 더해 {eok(m['ttm_equity'])} 위안, 주당 {m['ttm_eps']:.2f}위안, 배수는 {m['pe_ifrs']:.1f}배다. 비IFRS는 상반기 10% 성장률을 정확한 값으로 본 참고치라 주당 {m['ttm_non_ifrs_eps']:.1f}위안, {m['pe_non_ifrs']:.1f}배다.

## 12개월 주가 범위

2027년 10월을 본다. 그때 시장이 2027년 비IFRS 지배주주 순이익에 배수를 곱한다고 둔다. 주식 수는 {SHARES_MN/100:.2f}억 주로 고정했다. 자사주가 더 줄면 주당 가치는 같은 이익에서 그만큼 올라간다.

경로는 2025년 AI 제외 비IFRS 영업이익 {eok(filing.EX_AI_OP['FY25'])} 위안에서 출발한다.

| 경로 | AI 제외 영업이익 성장 | AI 적자 | 순이익 전환 | 2027년 추가 성장 | 이 경로의 배수 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 회수 | {pct(bull['ex_ai_g'], signed=True)} | {eok(bull['drag'])} | {pct(bull['drop'])} | {pct(bull['fy27_g'], signed=True)} | {bull['multiple']:.1f}배 |
| 유지 | {pct(base['ex_ai_g'], signed=True)} | {eok(base['drag'])} | {pct(base['drop'])} | {pct(base['fy27_g'], signed=True)} | {base['multiple']:.1f}배 |
| 부담 | {pct(bear['ex_ai_g'], signed=True)} | {eok(bear['drag'])} | {pct(bear['drop'])} | {pct(bear['fy27_g'], signed=True)} | {bear['multiple']:.1f}배 |

유지 경로의 배수는 오늘 비IFRS 배수 {m['pe_non_ifrs']:.1f}배를 그대로 쓴다. 회수는 16배, 부담은 9.5배다. 16배는 52주 고점 무렵의 IFRS 배수보다 낮다.

| 경로 | 2027년 비IFRS 지배순이익 | 주당 위안 | {matrix_header} |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(rows)}

각 경로에 그 경로의 배수를 곱한 주가는 다음과 같다.

- 회수: 홍콩달러 {bull['px_hkd']:.0f}원, 종가 대비 {pct(bull['upside'], signed=True)}. 새 앱 적자가 줄고 배수가 16배까지 회복하는 경우다.
- 유지: 홍콩달러 {base['px_hkd']:.0f}원, 종가 대비 {pct(base['upside'], signed=True)}. 이익은 늘고 배수는 오늘과 같다.
- 부담: 홍콩달러 {bear['px_hkd']:.0f}원, 종가 대비 {pct(bear['upside'], signed=True)}. 이익이 거의 늘지 않고 배수가 9.5배로 더 내려가는 경우다.

![12개월 시나리오 주가](price_scenarios.png)

기준점으로 삼을 숫자는 유지 경로의 약 {base['px_hkd']:.0f}홍콩달러다. 오늘 428홍콩달러와의 차이는 대부분 2년 치 이익 성장이다. 배수 회복을 가격에 넣지 않았다. 회수 경로 약 {bull['px_hkd']:.0f}홍콩달러는 이익과 배수가 같이 좋아지는 경우이고, 부담 경로 약 {bear['px_hkd']:.0f}홍콩달러는 설비 투자가 이익으로 바뀌기 전에 배수가 더 낮아지는 경우다. 세 숫자의 간격이 이 종목의 실제 불확실성이다.

외부 화면의 평균 목표가가 660홍콩달러 안팎인 곳이 있다. 그 가격은 52주 고가 664홍콩달러와 겹친다. 이 모델은 그 목표가를 쓰지 않는다.

## 이 범위가 깨지는 자리

10월 제안이 달러 5%대 채권으로 정해지면 그 회차의 금리 차이는 줄고, 위안 매출과의 통화 차이는 커진다. AI 적자가 2025년 174억 위안 쪽으로 다시 줄면 유지 경로의 이익이 회수 쪽으로 이동한다. 약정 2,802억 위안이 짧은 기간에 현금으로 나가면 순현금 582억은 소진되고, 부담 경로의 배수가 먼저 반응한다. 국내 게임 흥행이 빠지고 광고 성장이 10% 밑으로 내려가면 매출 가정의 출발점 자체가 달라진다.
"""


def main() -> None:
    setup_font()
    m = build()
    check(m)
    OUT.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    charts = [OUT / "price_scenarios.png", OUT / "funding_rates.png"]
    chart_prices(charts[0], m)
    chart_rates(charts[1], m)
    text = render(m)
    path = OUT / "outlook.md"
    path.write_text(text, encoding="utf-8")
    for chart in charts:
        shutil.copy(chart, ARTIFACTS / chart.name)
    shutil.copy(path, ARTIFACTS / "tencent-outlook-20261012.md")
    base = m["scenarios"]["유지"]
    print(f"종가 {PRICE_HKD:.0f} HKD / {m['price_rmb']:.1f} CNY")
    print(f"IFRS TTM PER {m['pe_ifrs']:.2f} / 비IFRS {m['pe_non_ifrs']:.2f}")
    print(f"위안 채권 쿠폰 {m['coupon']*100:.2f}%")
    print(f"달러 대비 이자 차이 {m['saving_vs_own_usd']/100:.1f}억")
    for name, sc in m["scenarios"].items():
        print(f"{name}: {sc['px_hkd']:.0f} HKD ({sc['upside']*100:+.1f}%) EPS {sc['eps27']:.2f}")
    print(path)


if __name__ == "__main__":
    main()
