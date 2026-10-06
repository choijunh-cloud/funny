#!/usr/bin/env python3
"""10월 2일 코멘트의 등식을 다시 계산하고, 방송에 써도 되는 문장만 남긴다.

가격·EPS·환율·비중은 원문 입력이다. 여기서 새로 추정하지 않는다.
판정은 세 가지다.
- 성립: 원문 문장과 계산이 맞다.
- 불성립: 원문 문장을 그대로 쓰면 안 되고, 계산 결과로 바꿔야 한다.
- 판단: 식이 아니라 시나리오다. 조건이 붙어야 쓸 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass, field


WON = 1
MAN = 10_000


def man(won: float, digits: int = 1) -> str:
    return f"{won / MAN:.{digits}f}만원"


def pct(x: float, digits: int = 1, signed: bool = True) -> str:
    sign = ""
    if x < 0:
        sign = "−"
    elif signed and x > 0:
        sign = "+"
    return sign + f"{abs(x) * 100:.{digits}f}%"


def roll_eps(q1: float, growth: tuple[float, ...] = (0.10, 0.05, 0.05)) -> float:
    """1분기 가이던스에 QoQ 성장률을 이어 붙여 연간 EPS를 만든다."""
    total = q1
    q = q1
    for g in growth:
        q *= 1 + g
        total += q
    return total


def asp_decline(floor_weight: float, market_drop: float, floor_pass: float = 0.5) -> float:
    """Floor 물량은 시장 하락의 floor_pass만 반영. 나머지는 시장가."""
    return floor_weight * (floor_pass * market_drop) + (1 - floor_weight) * market_drop


def revenue_change(asp: float, bit_growth: float) -> float:
    return (1 + asp) * (1 + bit_growth) - 1


def per(price_won: float, eps_won: float) -> float:
    return price_won / eps_won


@dataclass
class Check:
    id: str
    group: str
    verdict: str
    author: str
    computed: str
    on_air: str


@dataclass
class Insight:
    title: str
    thesis: str
    act: str
    confirm: str
    kill: str


@dataclass
class Audit:
    checks: list[Check] = field(default_factory=list)
    insights: list[Insight] = field(default_factory=list)

    def counts(self) -> dict[str, int]:
        out = {"성립": 0, "불성립": 0, "판단": 0}
        for c in self.checks:
            out[c.verdict] = out.get(c.verdict, 0) + 1
        return out


def build() -> Audit:
    # ── 원문 입력 (10/2) ──────────────────────────────────
    hynix_px = 1_842_000
    samsung_px = 276_000
    hynix_eps26, hynix_eps27 = 349_000, 444_000
    samsung_eps26, samsung_eps27 = 47_900, 67_900
    hynix_op26, hynix_op27 = 265.0, 392.0
    samsung_op26, samsung_op27 = 388.0, 555.0
    mu_px, mu_eps_fy, mu_eps_cy = 1074.89, 165.0, 180.0
    sndk_px, sndk_eps = 1719.99, 230.0
    adr_usd, fx = 195.13, 1347.0
    stx_px, stx_q1, stx_eps_claim = 848.99, 7.3, 32.6
    wdc_px, wdc_q1, wdc_eps_claim = 415.29, 4.0, 17.9

    # ── 계산 ──────────────────────────────────────────────
    adr_won = adr_usd * fx  # 1 ADR = 1본주로 둔 환산
    h26 = per(hynix_px, hynix_eps26)
    h27 = per(hynix_px, hynix_eps27)
    s26 = per(samsung_px, samsung_eps26)
    s27 = per(samsung_px, samsung_eps27)
    mu_fy = mu_px / mu_eps_fy
    mu_cy = mu_px / mu_eps_cy
    sndk_per = sndk_px / sndk_eps
    discount_vs_mu = h27 / mu_cy - 1

    stx_eps = roll_eps(stx_q1)
    wdc_eps = roll_eps(wdc_q1)
    stx_per = stx_px / stx_eps_claim
    wdc_per = wdc_px / wdc_eps_claim

    price_up = 122 / 100 - 1
    price_from_peak = 90 / 122 - 1
    price_from_now = 90 / 100 - 1
    sca = 0.35 * 0.75
    floor_w = 0.28 * 0.75
    asp20 = (asp_decline(0.20, 0.20), asp_decline(0.20, 0.30))
    asp21 = (asp_decline(floor_w, 0.20), asp_decline(floor_w, 0.30))

    rev_lo = revenue_change(-0.25, 0.15)
    rev_hi = revenue_change(-0.25, 0.20)
    bit_for_rev_minus_5 = 0.95 / 0.75 - 1

    # Base 박스의 네 귀퉁이. 피크 100~110조 → 28년 상반기 60~75조.
    corners = {
        "100→75": 75 / 100 - 1,
        "100→60": 60 / 100 - 1,
        "110→75": 75 / 110 - 1,
        "110→60": 60 / 110 - 1,
    }
    op_center = 67.5 / 105 - 1
    hist_template = (-0.80, -0.70)

    # 28년 EPS를 27년 44.4만원의 37% 감소로 두면 28.0만원.
    # 원문의 '20만원 후반'과 숫자가 맞지만, 키옥시아 60조의 세후 배분은 원문에 없다.
    eps28_from_27 = hynix_eps27 * (1 - 0.37)
    eps28_anchor = 280_000  # 원문 '20만원 후반'의 중심
    px_on_eps28 = {m: eps28_anchor * m for m in (4, 6, 8, 9)}
    now_on_eps28 = per(hynix_px, eps28_anchor)

    fx_cut = 1370 / 1480 - 1
    doosan = 1059 / 493 - 1
    intech_tp = 4904 * 19.4

    # 성호전자. 검색 PER 40~45배가 어떤 주식수인지는 원문이 확정하지 않는다.
    sungho_px = 31_200
    basic_sh, diluted_sh = 75.4e6, 111e6
    dilution = diluted_sh / basic_sh
    shinyoung_eps = 70_000 / 50  # 7만원 = 50배라면 EPS 1,400원
    # 케이스 D: 그 EPS가 이미 111백만주
    d_30, d_40 = shinyoung_eps * 30, shinyoung_eps * 40
    # 케이스 U: 1,400원이 75.4백만주 기준이면 희석 EPS
    u_eps = shinyoung_eps * basic_sh / diluted_sh
    u_30, u_40 = u_eps * 30, u_eps * 40
    # 케이스 S: 현재 검색 PER이 희석 전 27년 배수이고, 28년 이익이 2배
    s_band = []
    for per27 in (40, 45):
        eps27 = sungho_px / per27
        eps28_dil = eps27 * (basic_sh / diluted_sh) * 2
        s_band.append((per27, eps28_dil * 30, eps28_dil * 40, sungho_px / eps28_dil))

    # 앤트로픽. 891은 20% CAGR·FCF 마진 20%. 965를 같은 마진에서 맞추는 CAGR.
    base_ev, private_ev, ipo_ev = 891.0, 965.0, 2000.0
    cagr_for_private = 1.20 * (private_ev / base_ev) ** (1 / 7) - 1
    margin_only_ev = base_ev * (0.25 / 0.20)  # CAGR은 베이스와 동일, 마진만 25%
    platform_multiple = ipo_ev / margin_only_ev

    capex_1h = 25.0
    capex_fy_floor = capex_1h * 2  # 하반기가 상반기보다 크다는 문장

    bnk_2027, peer_2027 = 249.0, (389 + 397 + 406 + 426) / 4
    bnk_vs_peer = bnk_2027 / peer_2027 - 1
    # 2027년 249조이면서 4분기만 40조면 1~3분기 합은 209조
    bnk_q123 = (bnk_2027 - 40) / 3

    checks: list[Check] = [
        Check(
            "hynix-per",
            "메모리 밸류",
            "성립",
            "본주 26년 5.3배, 27년 4.1배",
            f"184.2만 / 34.9만 = {h26:.2f}배, / 44.4만 = {h27:.2f}배",
            "하이닉스 본주 184.2만원은 26년 EPS 5.3배, 27년 EPS 4.1배다. 이 4.1배는 27년 이익의 배수다.",
        ),
        Check(
            "samsung-per",
            "메모리 밸류",
            "성립",
            "삼성 26년 5.8배, 27년 4.1배",
            f"27.6만 / 4.79만 = {s26:.2f}배, / 6.79만 = {s27:.2f}배",
            "삼성전자 27.6만원은 26년 5.8배, 27년 4.1배다.",
        ),
        Check(
            "us-per",
            "메모리 밸류",
            "성립",
            "마이크론 FY 6.5배·CY 6.0배, 샌디스크 7.5배",
            f"MU {mu_fy:.2f}배 / {mu_cy:.2f}배, SNDK {sndk_per:.2f}배",
            f"마이크론 CY27은 {mu_cy:.1f}배, 샌디스크 FY27은 {sndk_per:.1f}배다. 미국 메모리는 6~7배다.",
        ),
        Check(
            "hynix-vs-mu",
            "메모리 밸류",
            "성립",
            "본주는 마이크론 대비 할인 30% 초반",
            f"27년 {h27:.2f}배 / 마이크론 {mu_cy:.2f}배 = {pct(discount_vs_mu)}",
            f"하이닉스 본주 27년 배수는 마이크론 CY27보다 {pct(-discount_vs_mu, signed=False)} 싸다. 비교는 본주로 한다.",
        ),
        Check(
            "growth",
            "메모리 밸류",
            "성립",
            "하이닉스 이익 +40%대, EPS +27%. 삼성 EPS +42%",
            (
                f"하이닉스 이익 {pct(hynix_op27 / hynix_op26 - 1)}, "
                f"EPS {pct(hynix_eps27 / hynix_eps26 - 1)}. "
                f"삼성 EPS {pct(samsung_eps27 / samsung_eps26 - 1)}"
            ),
            "컨센서스는 27년에도 증익이다. 하이닉스 영업이익 +48%, EPS +27%, 삼성 EPS +42%.",
        ),
        Check(
            "flat-multiple",
            "메모리 밸류",
            "성립",
            "26년 EPS에 6~7배면 하이닉스 209~244만, 삼성 28.7~33.5만",
            f"하이닉스 {man(hynix_eps26 * 6)}~{man(hynix_eps26 * 7)}, 삼성 {man(samsung_eps26 * 6, 1)}~{man(samsung_eps26 * 7)}",
            "27년 성장이 없다고 두면 26년 EPS 6~7배는 하이닉스 209~244만원, 삼성 28.7~33.5만원이다.",
        ),
        Check(
            "adr-fx",
            "ADR",
            "불성립",
            "ADR 195.13달러 = 263만원 (1,347원)",
            f"195.13 × 1,347 = {adr_won:,.0f}원 = {man(adr_won)}. ×10 = {man(adr_won * 10)}",
            "1,347원만 곱하면 26.3만원이다. 263만원은 여기에 10을 곱해야 나온다. 그 10은 원문에 없다. 1 ADR이 본주의 0.1주일 때의 배율이다.",
        ),
        Check(
            "adr-premium",
            "ADR",
            "판단",
            "본주 대비 44% 프리미엄. 30%면 202만, 20%면 219만",
            (
                f"배율 1: {man(adr_won)} / 184.2만 = {pct(adr_won / hynix_px - 1)}. "
                f"배율 10: {man(adr_won * 10)} / 184.2만 = {pct(adr_won * 10 / hynix_px - 1)}, "
                f"30%면 {man(adr_won * 10 / 1.30)}, 20%면 {man(adr_won * 10 / 1.20)}"
            ),
            "배율 10이면 프리미엄은 43%이고, 30%로 좁히면 본주 202만원, 20%면 219만원이다. 배율 1이면 그 레벨은 폐기하고 ADR은 본주 대비 86% 할인이 된다. 배율을 확인하기 전에는 202만·219만을 목표로 확정하지 않는다.",
        ),
        Check(
            "adr-per",
            "ADR",
            "판단",
            "ADR 26년 7.5배, 27년 5.9배, 마이크론과 동급",
            f"배율 10이면 {per(adr_won * 10, hynix_eps26):.2f}배 / {per(adr_won * 10, hynix_eps27):.2f}배. 배율 1이면 {per(adr_won, hynix_eps26):.2f}배",
            "7.5배·5.9배와 ‘마이크론과 동급’은 배율 10일 때만 맞다. 배율과 무관하게 쓸 비교는 본주 27년 4.1배 대 마이크론 6.0배, 할인 약 31%다.",
        ),
        Check(
            "normalized-multiple",
            "28년 가치",
            "성립",
            "정상화 EPS 20만원 후반 × 8~9배 = 220~250만원",
            f"28만원 × 8 = {man(px_on_eps28[8])}, × 9 = {man(px_on_eps28[9])}. 현재가는 그 EPS의 {now_on_eps28:.1f}배",
            "220~250만원은 28년 EPS 28만원에 8~9배를 준 자리다. 현재 184만원은 같은 EPS의 6.6배다. 4.1배라는 싸 보임은 27년 이익 기준이다.",
        ),
        Check(
            "eps28-link",
            "28년 가치",
            "판단",
            "일회성을 빼면 28년 EPS는 20만원 후반",
            f"27년 EPS 44.4만 × (1−37%) = {man(eps28_from_27)}. 키옥시아 60조의 세후 공식은 원문에 없다",
            "28만원은 검증된 회계 등식이 아니다. 27년 EPS가 약 37% 줄면 28만원이 되고, 피크 분기 105조에서 67조로 줄면 이익도 약 36% 준다. 이 입력을 쓸 때만 220~250만원이 따라온다.",
        ),
        Check(
            "downside-band",
            "28년 가치",
            "성립",
            "과거 사이클 배수는 4~8배",
            f"EPS 28만원에 4배 {man(px_on_eps28[4])}, 6배 {man(px_on_eps28[6])}, 8배 {man(px_on_eps28[8])}",
            "28년 EPS가 28만원이어도 배수를 4~6배에 두면 112~168만원이다. 현재가보다 낮다. 업사이드는 8배 이상으로 재평가될 때 열린다.",
        ),
        Check(
            "price-path",
            "가격 경로",
            "성립",
            "100 → 122 → 90, 피크 대비 약 −26%",
            f"상승 {pct(price_up)}, 피크 대비 {pct(price_from_peak)}, 현재 대비 {pct(price_from_now)}",
            "가격은 6~9개월 +22%, 피크 이후 1년 −26%, 오늘보다 −10%를 기본 경로로 둔다.",
        ),
        Check(
            "sca",
            "가격 경로",
            "성립",
            "2030년 매출의 약 26.25%가 가격 프레임",
            f"35% × 75% = {sca * 100:.2f}%",
            "SCA가 가격을 멈추지는 않는다. 2030년 매출의 26%만 미리 정한 가격 밴드 안에 있다.",
        ),
        Check(
            "asp",
            "가격 경로",
            "성립",
            "평균 ASP −18~−27%",
            (
                f"Floor 20%면 {pct(-asp20[1])}~{pct(-asp20[0])}. "
                f"Floor 21%면 {pct(-asp21[1])}~{pct(-asp21[0])}"
            ),
            "시장가 −20~−30%, Floor는 그 절반, Floor 비중 20%면 평균 ASP는 −18~−27%다. LTA가 있어도 가격은 두 자릿수로 빠질 수 있다.",
        ),
        Check(
            "revenue-bridge",
            "가격 경로",
            "불성립",
            "ASP −25%, 비트 +15~20%면 매출 −5~−10%",
            f"매출 {pct(rev_lo)}~{pct(rev_hi)}. 매출 −5%에 필요한 비트 성장은 {pct(bit_for_rev_minus_5)}",
            "ASP −25%와 비트 +15~20%를 같이 쓰면 매출은 −14~−10%다. 매출 −5%를 말하려면 비트 성장 +27%가 필요하다.",
        ),
        Check(
            "op-vs-price",
            "가격 경로",
            "불성립",
            "28년 상반기 이익은 가격보다 덜 빠진다",
            (
                f"가격 {pct(price_from_peak)}. 이익 귀퉁이 "
                + ", ".join(f"{k} {pct(v)}" for k, v in corners.items())
                + f". 한복판 {pct(op_center)}. 과거 템플릿 {pct(hist_template[0])}~{pct(hist_template[1])}"
            ),
            "과거 공식(가격 −25%일 때 이익 −70~−80%)보다는 완만하다. Base 한복판은 피크 대비 이익 −36%로, 가격 −26%보다 이익이 더 준다. '가격보다 덜'은 과거 사이클과 비교할 때만 쓴다.",
        ),
        Check(
            "op-example",
            "가격 경로",
            "판단",
            "65~75조가 피크 100~110조, 28년 상반기 60~75조",
            "현재 70조의 +50% = 105조. 이는 예시이지 회사 가이던스가 아니다",
            "말할 경로의 중심은 분기 70조 → 100~110조 → 60~75조다. 40조 이하는 가격 급락, 비트 둔화, HBM 가격 하락, 공급 증가, Floor 무력화가 같이 올 때다.",
        ),
        Check(
            "bnk",
            "가격 경로",
            "판단",
            "BNK 4Q27 40조 이하는 가격 반토막(−43%)",
            (
                f"−43%면 가격지수 57, 반토막은 50이다. "
                f"2027년 249조에서 4분기 40조를 빼면 1~3분기 평균 {bnk_q123:.0f}조. "
                f"동종 2027년 평균 {peer_2027:.0f}조 대비 {pct(bnk_vs_peer)}"
            ),
            "40조는 산술적으로 불가능하지 않다. BNK 2027년 249조는 동종 평균보다 이미 38% 낮다. 극단으로 두는 이유는 반토막이라는 말 때문이 아니라, 이 경로가 동종 대비 낮은 2027년 위에 있기 때문이다. 가격 하락 입력은 −43%로 말한다.",
        ),
        Check(
            "capex",
            "가격 경로",
            "판단",
            "CapEx 500억 달러",
            f"상반기 250억 달러, 하반기가 그보다 크면 연간은 {capex_fy_floor * 10:.0f}억 달러를 넘는다. 1분기 115억 달러는 상반기 250억 달러와 모순되지 않는다",
            "500억 달러는 라운드 넘버로 읽고, 연간은 그 위일 수 있다고 말한다. 건물과 장비를 나누는 결론은 그대로 쓴다. 장비는 수요 확인 뒤로 미룬다.",
        ),
        Check(
            "fx",
            "환율",
            "판단",
            "1,480원 → 1,370원이면 컨센서스 약 −10%",
            f"1,370/1,480 − 1 = {pct(fx_cut)}",
            "환율 가정만 바꾸면 1차 효과는 −7.4%다. −10%는 전가와 믹스까지 넣은 버퍼로만 말한다.",
        ),
        Check(
            "hdd-eps",
            "HDD",
            "성립",
            "STX FY27 EPS 32.6달러 PER 26배, WDC 17.9달러 PER 23배",
            f"롤포워드 STX {stx_eps:.2f} (PER {stx_px / stx_eps:.1f}), WDC {wdc_eps:.2f} (PER {wdc_px / wdc_eps:.1f}). 원문 EPS로 PER {stx_per:.1f} / {wdc_per:.1f}",
            "가이던스에 +10%, +5%, +5%를 붙이면 Seagate EPS 32.6달러, PER 26배, WDC EPS 17.9달러, PER 23배가 맞다.",
        ),
        Check(
            "hdd-share",
            "HDD",
            "성립",
            "도시바 14% → 30%면 상위 둘 합산 86% → 70%",
            "45+41+14=100. 점유율 +16%p를 둘에게서 빼면 86−16=70",
            "점유율 산수는 86%에서 70%다. 물량이 1:1로 잠식되는지는 수요 증가가 결정한다. 2026~27년 이미 팔린 물량을 오늘 깨는 뉴스는 아니다.",
        ),
        Check(
            "doosan",
            "광 · 두산",
            "성립",
            "광모듈 CCL 493억 → 1,059억, QoQ +115%",
            f"1,059/493 − 1 = {pct(doosan)}",
            "두산 광모듈 CCL 3분기 1,059억, 전분기 대비 +115%는 계산이 맞다. 규제 헤드라인과 이 매출은 다른 층이다.",
        ),
        Check(
            "sungho-tp",
            "성호전자",
            "불성립",
            "28년 PER 30~40배의 하단이 5~6만원 중반",
            (
                f"7만원/50배 = EPS {shinyoung_eps:,.0f}원. "
                f"이미 희석됐다면 30배 {d_30:,.0f}원, 40배 {d_40:,.0f}원. "
                f"1,400원이 희석 전이면 EPS {u_eps:,.0f}원, 30배 {u_30:,.0f}원, 40배 {u_40:,.0f}원"
            ),
            "5~6만원 중반은 30배의 하단이 아니다. EPS 1,400원이 이미 111백만주면 30배는 4.2만원, 40배는 5.6만원이다. 1,400원이 희석 전이면 30~40배는 2.9~3.8만원이다.",
        ),
        Check(
            "sungho-screen",
            "성호전자",
            "판단",
            "10/2 주가 31,200원, 27년 PER 40~45배, 이후 100% 성장",
            (
                "검색 PER을 희석 전으로 보고 28년 2배를 희석하면 "
                + ", ".join(
                    f"27년 {p}배 → 현재가는 희석 28년 {m:.0f}배, 30배 {a:,.0f}원, 40배 {b:,.0f}원"
                    for p, a, b, m in s_band
                )
            ),
            "검색 PER 40~45배가 희석 전이면, 이익이 두 배가 돼도 현재 3.12만원은 이미 희석 28년 29~33배다. 희석이 반영된 PER이면 30배는 4.2~4.7만원이다. 주수를 확인하기 전에는 한 목표가로 말하지 않는다.",
        ),
        Check(
            "dilution",
            "성호전자",
            "성립",
            "75.4백만주 → 전환 시 111백만주",
            f"주식수 {pct(dilution - 1)}, EPS는 {basic_sh / diluted_sh:.3f}배",
            "전환이 끝나면 주식수는 47% 늘고, 같은 순이익의 EPS는 32% 준다. PER은 111백만주로 나눈다.",
        ),
        Check(
            "intech",
            "장중 실명",
            "성립",
            "인텍플러스 목표 9.5만원 = EPS 4,904원 × 19.4배",
            f"4,904 × 19.4 = {intech_tp:,.0f}원",
            "인텍플러스 9.5만원은 주어진 EPS와 19.4배의 곱과 맞다. 수주잔고 1,700억과 4분기 신규 1,000억은 인용이다.",
        ),
        Check(
            "portfolio",
            "장중 실명",
            "성립",
            "AI 50~60%(삼전닉스 30~40 + 소부장 20), 2차전지 10, 건설조선 10, 현금 20",
            "30+20+10+10+20=90이 아니라 소부장 20은 AI 50의 안이다. 코너 30+20+10+10+20=100, 40+20+10+10+20=100",
            "소부장은 AI 비중 안에 있다. 삼전닉스 30% 또는 40%의 양 끝에서 합이 100이 된다. 중간을 쓰면 현금이 20%를 넘긴다.",
        ),
        Check(
            "anthropic-base",
            "앤트로픽",
            "성립",
            "FCF 마진 20%면 약 8,910억 달러. 9,650억에는 CAGR 21.4%가 필요",
            f"20%에서 7년, EV가 965/891배가 되려면 CAGR {pct(cagr_for_private, digits=2)}",
            f"베이스 8,910억 달러에서 사모가치 9,650억 달러를 같은 마진으로 맞추면 2029~35년 CAGR은 {cagr_for_private * 100:.1f}%다. 원문의 21.4%와 맞다.",
        ),
        Check(
            "anthropic-bull",
            "앤트로픽",
            "불성립",
            "FCF 마진 25%와 연 20% 성장이면 IPO 2조 달러",
            f"마진만 20%→25%면 EV 약 {margin_only_ev:,.0f}억 달러. 2조 / 그 값 = {platform_multiple:.2f}배",
            "마진 25%와 성장 20%만으로는 약 1.1조 달러다. 2조 달러는 그 위에 플랫폼 배수가 약 1.8배 더 붙어야 한다. 2조는 플랫폼 프리미엄의 자리다.",
        ),
    ]

    # 손 계산과 코드가 어긋나면 여기서 멈춘다.
    assert abs(adr_won - 262_840.11) < 1
    assert abs(sca - 0.2625) < 1e-12
    assert abs(asp20[0] - 0.18) < 1e-12 and abs(asp20[1] - 0.27) < 1e-12
    assert abs(rev_lo - (0.75 * 1.15 - 1)) < 1e-12
    assert abs(rev_hi - (0.75 * 1.20 - 1)) < 1e-12
    assert abs(stx_eps - 32.6145) < 1e-3
    assert abs(wdc_eps - 17.871) < 1e-3
    assert abs(doosan - (1059 / 493 - 1)) < 1e-12
    assert abs(intech_tp - 95_137.6) < 1e-6
    assert abs(cagr_for_private - 0.214) < 0.001
    assert abs(h26 - 5.278) < 0.01
    assert abs(now_on_eps28 - 6.579) < 0.01
    assert shinyoung_eps == 1_400

    insights = [
        Insight(
            title="지수는 10년물, 알파는 AI",
            thesis="9월 고용 +2.9만은 침체 진입이 아니라 완만한 둔화다. 임금 YoY 3.0%, 근원 PCE 3.0~3.2%라 10월은 동결 쪽이고 인하 재료는 아니다. 당일 SOX +2.4%와 10년물 5.28%가 같이 나왔다.",
            act="지수 베타는 10년물 5%대에서 과감히 늘리지 않는다. 추가 위험은 AI 직간접에 둔다. 신규는 분할이다. 유가 100달러 위는 그 분할을 유지하는 조건이다.",
            confirm="10년물이 추세적으로 5% 아래로 내려오고 고용이 이 둔화 속도에 머문다.",
            kill="12월 인상 확률이 다시 올라오거나, 고용이 침체로 재분류될 만큼 임금까지 꺾인다.",
        ),
        Insight(
            title="하이닉스를 사는 이유는 4.1배가 아니다",
            thesis=f"184.2만원은 27년 EPS의 {h27:.1f}배이고, 28년 EPS 28만원을 가정하면 이미 {now_on_eps28:.1f}배다. 220~250만원은 그 28만원에 8~9배를 붙일 때 나온다. 4~6배면 112~168만원으로 현재보다 낮다.",
            act="매수 문장은 ‘피크 이익이 싸다’가 아니라 ‘28년 정상화 EPS가 28만원 근처로 남고, 시장이 8배 이상을 준다’이다. 8배의 첫 관문은 224만원, 현재 대비 약 +22%다. 27년 3월까지는 계단으로 보고, 금리가 숨통을 틀 때 폭을 키운다.",
            confirm="28년에도 분기 영업이익이 60조 위에 남는다는 증거가 수주·HBM 믹스·Floor에서 나온다.",
            kill="분기 이익이 40조 경로(BNK: 2027년 249조, 동종 대비 약 −38%)로 내려가면 8배 가정은 폐기한다.",
        ),
        Insight(
            title="피크 이후 손익은 이렇게만 말한다",
            thesis=f"가격 100→122→90은 +22%, 피크 대비 {pct(price_from_peak)}다. Floor 20%면 평균 ASP는 −18~−27%다. ASP −25%와 비트 +15~20%면 매출은 {pct(rev_lo)}~{pct(rev_hi)}다. Base 한복판의 이익은 피크 대비 약 −36%다.",
            act="매출 −5%와 ‘이익이 가격보다 덜 빠진다’는 문장은 뺀다. 남길 문장은 하나다. 과거처럼 −70~−80%까지 무너지는 공식은 기본 경로가 아니고, 그래도 피크 대비 이익 감소는 가격 감소보다 크다.",
            confirm="비트 성장이 +27%에 가까우면 그때 매출 감소는 −5% 안쪽으로 들어온다.",
            kill="Floor 비중이 가정(매출의 약 21%)보다 낮거나, 비트 성장이 +15%를 밑돈다.",
        ),
        Insight(
            title="ADR은 배율을 적고 나서 말한다",
            thesis=f"195.13달러 × 1,347원 = {man(adr_won)}이다. 263만원은 이 값의 10배다. 10은 1 ADR = 본주 0.1주일 때의 배율이고, 8월 18일 노트도 같은 10배가 숨어 있다.",
            act="배율 10이면 프리미엄 43%, 30%로 좁히면 본주 202만원, 20%면 219만원이다. 배율 1이면 그 목표를 폐기한다. 배율 확인 전에는 본주 27년 4.1배 대 마이크론 6.0배, 할인 약 31%만 상대가치로 쓴다.",
            confirm="ADR 1주가 본주 0.1주라는 비율이 호가 정의와 맞다.",
            kill="비율을 적지 않은 채 202만원·219만원을 확정 목표로 말하는 것.",
        ),
        Insight(
            title="HDD와 메모리는 같은 하락이 아니다",
            thesis="Seagate PER 26배, WDC PER 23배는 가이던스 롤포워드와 맞다. 도시바 3.8억 달러는 FY2027 캐파 2배이고, 가격 영향은 2028년 이후다. 점유율 산수만 86%→70%다.",
            act="−10%를 당일 공급과잉으로 받지 않는다. 동시에 메모리처럼 한 자릿수 PER이라 싸다고 받지도 않는다. 재평가로 올라온 20배대의 압축이 리스크다.",
            confirm="2026~27년 장기계약 물량이 유지되고, ASP 가이던스가 유지된다.",
            kill="니어라인 계약이 깨지거나, 도시바 증설 일정이 2027년 안으로 앞당겨진다.",
        ),
        Insight(
            title="광은 다음 병목, 두산 급락은 과민, 성호는 주수 다음이다",
            thesis="수혜 순서는 GPU → HBM → 스위치 → Copper → Optical → CPO다. 중국 규제는 3.2T 공급망을 미국 DSP·레이저 중심으로 설계하는 이야기다. 두산 CCL은 3분기 1,059억, QoQ +115%다.",
            act="두산은 광모듈 규제 헤드라인으로 팔지 않는다. 성호전자는 액티브 정렬이라는 노출만 먼저 확정한다. 가격은 두 칸으로 말한다. EPS 1,400원이 이미 희석이면 30배 4.2만원·40배 5.6만원. 희석 전이면 30~40배는 2.9~3.8만원이고 현재 3.12만원은 그 안에 걸친다. 7만원은 50배라 현재 목표로 쓰지 않는다.",
            confirm="CPO 양산이 루빈 울트라 일정에 남고, 컨센서스 주식수가 111백만주인지가 확인된다.",
            kill="POET식 정렬 생략이 양산 공급망에 들어가거나, CPO 일정이 밀리거나, 희석 전 EPS로 5~6만원을 하단이라고 말하는 것.",
        ),
        Insight(
            title="위성 포지션과 수요 온도계",
            thesis="포트 코너는 삼전닉스 30% 또는 40%에 소부장 20%를 더해 AI 50~60%, 2차전지 10%, 건설·조선 10%, 현금 20%다. 인텍플러스 9.5만원은 EPS×배수가 맞다. 산일전기는 FY28 16배로 대형 변압기 31배보다 낮고, 이익 CAGR이 매출 CAGR보다 높다. 앤트로픽 2조 달러는 마진 25%만으로 안 나오고 플랫폼 배수 약 1.8배가 더 필요하다.",
            act="변압기는 산일전기를 1순위로 둔다. 기판의 단기 탄력은 가벼운 이름, 삼성전기는 눌림에서 본다. 앤트로픽·오픈AI는 토큰 수요의 온도계로만 쓰고 상장 주식의 목표가로 쓰지 않는다. 규제 차이는 접근권에 남아 있고, 안전장치 쪽 간극은 좁아지는 중이다.",
            confirm="인텍플러스 잔고가 1,700억으로 확인되고, 산일 154kV 수주가 숫자로 나온다. 에이전트 제품의 사용량이 토큰 10배→15배→20배 질문을 채운다.",
            kill="현금 20%를 지키지 못하고 AI를 60% 위에 더 쌓는 것. 앤트로픽 2조를 베이스 수요로 메모리 이익에 반영하는 것.",
        ),
    ]

    audit = Audit(checks=checks, insights=insights)
    # 판정 라벨이 세 가지 안에 있는지만 확인한다.
    for c in audit.checks:
        assert c.verdict in {"성립", "불성립", "판단"}
        assert c.on_air
    assert len(audit.insights) == 7
    return audit


def render_report(audit: Audit) -> str:
    counts = audit.counts()
    lines = [
        "10월 2일 검증",
        f"성립 {counts['성립']}  불성립 {counts['불성립']}  판단 {counts['판단']}  합계 {len(audit.checks)}",
        "",
    ]
    group = None
    for c in audit.checks:
        if c.group != group:
            group = c.group
            lines.append(f"## {group}")
        lines.append(f"[{c.verdict}] {c.id}")
        lines.append(f"  원문: {c.author}")
        lines.append(f"  계산: {c.computed}")
        lines.append(f"  방송: {c.on_air}")
        lines.append("")
    lines.append("## 증류")
    for i, ins in enumerate(audit.insights, 1):
        lines.append(f"{i}. {ins.title}")
        lines.append(f"  {ins.thesis}")
        lines.append(f"  실행: {ins.act}")
        lines.append(f"  확인: {ins.confirm}")
        lines.append(f"  폐기: {ins.kill}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    audit = build()
    print(render_report(audit))


if __name__ == "__main__":
    main()
