# -*- coding: utf-8 -*-
"""
톤즈 부평점 인수 딜 정밀 추정 모델
====================================
대화에서 확정된 검증식을 그대로 코드화한 뒤,
물리적 환자 수용력과 운영 리스크를 몬테카를로로 얹어 추정한다.

확정 가정 (검증식):
  - 부부 몫: 매출의 10% 선취 (세전)
  - 1인 세후 실수령 = 월매출 x 3.1%  (실효세율 약 38% 반영)
  - 변동비: 매출의 30% (재료비 + 카드수수료 등)
  - 고정비: 직원 50명 반영 연 70억 중심 (의사 8~10명 + 직원 50명 + 임대 + 마케팅 + 기타)
  - MSO가 OPEX 전액 부담, 잔여 현금흐름으로 90억 상환 (기본 무이자, 6% 변형 포함)
  - 물리 용량: 월매출 = 의사수 x 의사당 일환자 x 객단가 x 월 28일 가동
"""

import numpy as np

# ---------------------------------------------------------------
# 0. 공통 파라미터
# ---------------------------------------------------------------
DEBT = 90.0                 # 상환 원금 (억)
COUPLE_SHARE = 0.10         # 부부 선취율 (매출 대비)
NET_COEF_PER_PERSON = 0.031 # 1인 세후 = 월매출 x 3.1% (검증식)
VAR_RATE_BASE = 0.30        # 변동비율
FIXED_BASE = 70.0           # 연 고정비 중심값 (억) — 직원 50명 반영
WORK_DAYS = 28              # 월 가동일 (월 2일 휴무)

# MSO 마진율: 매출 1원당 상환 재원 = 0.9 - 변동비율
def mso_annual_surplus(monthly_rev, fixed=FIXED_BASE, var_rate=VAR_RATE_BASE):
    """연간 상환여력 (억). monthly_rev: 월매출(억)"""
    return 12.0 * monthly_rev * (0.9 - var_rate) - fixed

def required_monthly_rev(annual_payment, fixed=FIXED_BASE, var_rate=VAR_RATE_BASE):
    """연 상환액을 만들기 위해 필요한 월매출 (억)"""
    return (fixed + annual_payment) / (12.0 * (0.9 - var_rate))

def annuity_payment(principal, rate, years):
    """이자부 상환 시 연 원리금 (억)"""
    if rate == 0:
        return principal / years
    return principal * rate / (1.0 - (1.0 + rate) ** (-years))

def couple_net_monthly(monthly_rev):
    """부부 합산 월 세후 실수령 (억)"""
    return monthly_rev * NET_COEF_PER_PERSON * 2

FMT_MAN = lambda eok: f"{eok*10000:,.0f}만"   # 억 -> 만원 표기


# ---------------------------------------------------------------
# 1. 결정론적 BEP / 완제선 (검증식 그대로)
# ---------------------------------------------------------------
def deterministic_section():
    print("=" * 72)
    print("[1] 결정론적 BEP / 완제선  (고정비 시나리오별, 변동비 30%, 무이자)")
    print("=" * 72)
    header = f"{'고정비(연)':>10} | {'운영BEP':>8} | {'10년완제':>8} | {'7년완제':>8} | {'6년완제':>8}"
    print(header)
    print("-" * len(header))
    for fixed in (58.0, 64.0, 70.0, 75.0):
        bep = required_monthly_rev(0, fixed)
        r10 = required_monthly_rev(DEBT / 10, fixed)
        r7 = required_monthly_rev(DEBT / 7, fixed)
        r6 = required_monthly_rev(DEBT / 6, fixed)
        print(f"{fixed:>9.0f}억 | {bep:>7.2f}억 | {r10:>7.2f}억 | {r7:>7.2f}억 | {r6:>7.2f}억")

    print("\n  * 이자 6% 가정 시 (고정비 70억):")
    for years in (7, 10):
        pay = annuity_payment(DEBT, 0.06, years)
        req = required_monthly_rev(pay, 70.0)
        print(f"    - {years}년 원리금 연 {pay:.1f}억 → 필요 월매출 {req:.2f}억 "
              f"(총지불 {pay*years:.0f}억)")


# ---------------------------------------------------------------
# 2. 물리 용량 그리드: 일환자 x 객단가 → 월매출 / 실수령 / 엑시트
# ---------------------------------------------------------------
def capacity_grid_section():
    print("\n" + "=" * 72)
    print("[2] 물리 용량 역산 그리드  (의사 10명, 월 28일, 고정비 70억)")
    print("=" * 72)
    print(f"{'의사당 일환자':>8} | {'일 총환자':>7} | {'객단가':>6} | {'월매출':>7} | "
          f"{'부부 월실수령':>10} | {'연 상환여력':>9} | {'완제 소요':>8}")
    print("-" * 88)
    for ppd in (20, 22, 25, 28, 30, 32, 35):
        for price in (12, 14, 15, 16):  # 객단가 (만원)
            rev = 10 * ppd * price * WORK_DAYS / 10000  # 억/월
            surplus = mso_annual_surplus(rev, 70.0)
            net = couple_net_monthly(rev)
            if surplus > 0:
                exit_y = DEBT / surplus
                exit_s = f"{exit_y:>6.1f}년" if exit_y <= 30 else "  30년+"
            else:
                exit_s = "   불가"
            if price in (14, 15) or ppd in (25, 28):
                print(f"{ppd:>10}명 | {ppd*10:>6}명 | {price:>4.0f}만 | "
                      f"{rev:>6.2f}억 | {FMT_MAN(net):>10} | "
                      f"{surplus:>+8.1f}억 | {exit_s}")


# ---------------------------------------------------------------
# 3. 몬테카를로 시뮬레이션
# ---------------------------------------------------------------
def run_monte_carlo(n_paths=50_000, horizon_years=15, interest=0.0, seed=42,
                    legal_annual=0.015):
    """
    월 단위 15년 시뮬레이션.
    반환: dict (exit 연도 배열, 정상상태 월매출, 부부 실수령, 파산/법적사고 플래그 등)
    """
    rng = np.random.default_rng(seed)
    months = horizon_years * 12

    # ---- 경로별 정적 파라미터 ----
    # 의사 수: 8/9/10명 (인력 유지 난이도 반영)
    n_doc = rng.choice([8, 9, 10], size=n_paths, p=[0.25, 0.35, 0.40]).astype(float)

    # 의사당 일 환자수 (실현 수요): 중앙 25명, p10~19 / p90~31, 물리상한 35
    ppd = rng.lognormal(mean=np.log(25.0), sigma=0.19, size=n_paths)
    ppd = np.clip(ppd, 12.0, 35.0)

    # 객단가 (만원): 중앙 14, 11~17
    price = rng.normal(14.0, 1.5, size=n_paths)
    price = np.clip(price, 10.0, 18.0)

    # 고정비 (연, 억): 중심 70, 표준편차 4
    fixed = np.clip(rng.normal(FIXED_BASE, 4.0, size=n_paths), 60.0, 82.0)

    # 변동비율: 중심 30%
    var_rate = np.clip(rng.normal(0.30, 0.02, size=n_paths), 0.25, 0.36)

    # 인수 직후 램프: 기존 운영 병원 인수 + 황아름 잔류 → 완만한 전환 딥
    ramp_start = rng.uniform(0.75, 1.00, size=n_paths)
    ramp_months = rng.integers(4, 13, size=n_paths)

    # 정상상태 월매출 (억)
    steady_rev = n_doc * ppd * price * WORK_DAYS / 10000.0

    # ---- 이벤트 해저드 (월 단위 확률) ----
    p_doc_leave = 0.40 / 12          # 의사 1명 이탈: 연 0.4회, 공백 3~9개월 -1명
    p_founder_exit = 0.05 / 12       # 황아름 이탈 (2년차 이후): 영구 매출 -15%
    p_burnout = 0.10 / 12            # 부부 번아웃/강도저하 (3년차 이후): 영구 -8%
    p_legal = legal_annual / 12      # 사무장병원 등 법적 사고: 소유권 실패 처리

    balance = np.full(n_paths, DEBT)          # 잔여 부채
    cash = np.zeros(n_paths)                  # 누적 적자 이월 (음수면 적자 메꿔야 함)
    exit_month = np.full(n_paths, np.inf)
    legal_hit = np.zeros(n_paths, dtype=bool)
    founder_mult = np.ones(n_paths)
    burnout_mult = np.ones(n_paths)
    doc_gap_until = np.zeros(n_paths, dtype=int)   # 의사 공백 종료 월
    monthly_rate = (1 + interest) ** (1 / 12) - 1 if interest > 0 else 0.0

    # 정상상태(13~24개월차) 매출·실수령 기록용
    rev_record = np.zeros(n_paths)
    rec_cnt = 0

    ar_noise = np.zeros(n_paths)
    for m in range(months):
        active = np.isinf(exit_month) & ~legal_hit
        if not active.any():
            break

        # 램프업 계수
        ramp = np.minimum(1.0, ramp_start + (1 - ramp_start) * np.minimum(m / np.maximum(ramp_months, 1), 1.0))

        # 계절성 (±7%) + AR(1) 노이즈 (sigma 6%)
        season = 1.0 + 0.07 * np.sin(2 * np.pi * (m % 12) / 12.0)
        ar_noise = 0.6 * ar_noise + rng.normal(0, 0.06, n_paths)
        noise = np.exp(ar_noise - 0.5 * 0.06**2 / (1 - 0.6**2))

        # 이벤트 발생
        u = rng.random(n_paths)
        leave = (u < p_doc_leave) & active
        doc_gap_until[leave] = m + rng.integers(3, 10, size=leave.sum())
        if m >= 24:
            u2 = rng.random(n_paths)
            founder_mult[(u2 < p_founder_exit) & active & (founder_mult == 1.0)] = 0.85
        if m >= 36:
            u3 = rng.random(n_paths)
            burnout_mult[(u3 < p_burnout) & active & (burnout_mult == 1.0)] = 0.92
        u4 = rng.random(n_paths)
        legal_hit |= (u4 < p_legal) & active

        # 의사 공백 반영 (1명 빠진 비율만큼 매출 감소)
        gap_factor = np.where(m < doc_gap_until, (n_doc - 1) / n_doc, 1.0)

        rev = steady_rev * ramp * season * noise * gap_factor * founder_mult * burnout_mult

        if 12 <= m < 24:
            rev_record += rev
            rec_cnt += 1

        # MSO 월 현금흐름 = 0.9R - 변동비 - 고정비/12
        surplus = rev * (0.9 - var_rate) - fixed / 12.0

        # 이자 (이자부 시나리오)
        if monthly_rate > 0:
            balance[active] *= (1 + monthly_rate)

        # 적자 이월: cash가 0 이상이 된 뒤에야 상환
        cash[active] += surplus[active]
        pay = np.maximum(np.minimum(cash, balance), 0.0)
        pay[~active] = 0.0
        balance -= pay
        cash -= pay

        done = active & (balance <= 1e-9)
        exit_month[done] = m + 1

    steady_rev_realized = rev_record / max(rec_cnt, 1)
    exit_years = exit_month / 12.0

    return {
        "exit_years": exit_years,
        "legal_hit": legal_hit,
        "steady_rev": steady_rev_realized,
        "couple_net": couple_net_monthly(steady_rev_realized),
        "op_surplus": mso_annual_surplus(steady_rev_realized, fixed, var_rate),
    }


def mc_section():
    print("\n" + "=" * 72)
    print("[3] 몬테카를로 시뮬레이션  (50,000 경로 x 15년, 월 단위)")
    print("=" * 72)

    scenarios = (
        ("무이자 (90억 캡)", 0.0, 0.015),
        ("이자 6% (원리금)", 0.06, 0.015),
        ("무이자 + 법적리스크 제외 (분해용)", 0.0, 0.0),
    )
    for label, interest, legal in scenarios:
        r = run_monte_carlo(interest=interest, legal_annual=legal)
        ey, legal = r["exit_years"], r["legal_hit"]
        ok = ~legal
        # 법적 사고 경로는 소유권 실패로 처리
        p6 = np.mean((ey <= 6) & ok) * 100
        p7 = np.mean((ey <= 7) & ok) * 100
        p10 = np.mean((ey <= 10) & ok) * 100
        p15 = np.mean((ey <= 15) & ok) * 100
        fin = ey[ok & np.isfinite(ey)]
        med = np.median(fin) if len(fin) else float("nan")

        print(f"\n--- {label} ---")
        print(f"  6년 내 완제 확률   : {p6:5.1f}%")
        print(f"  7년 내 완제 확률   : {p7:5.1f}%")
        print(f" 10년 내 완제 확률   : {p10:5.1f}%")
        print(f" 15년 내 완제 확률   : {p15:5.1f}%")
        print(f"  완제 성공 경로의 중앙 소요기간: {med:.1f}년")
        print(f"  법적 사고(사무장 등) 경로 비중: {legal.mean()*100:.1f}%")

        if interest == 0.0:
            rev = r["steady_rev"]
            net = r["couple_net"]
            surplus = r["op_surplus"]
            q = lambda a, p: np.percentile(a, p)
            print(f"\n  [정상상태 (2년차) 월매출 분포]")
            print(f"    p10 {q(rev,10):.1f}억 | p25 {q(rev,25):.1f}억 | 중앙 {q(rev,50):.1f}억 "
                  f"| p75 {q(rev,75):.1f}억 | p90 {q(rev,90):.1f}억")
            print(f"  [부부 합산 월 세후 실수령 분포]")
            print(f"    p10 {FMT_MAN(q(net,10))} | p25 {FMT_MAN(q(net,25))} | 중앙 {FMT_MAN(q(net,50))} "
                  f"| p75 {FMT_MAN(q(net,75))} | p90 {FMT_MAN(q(net,90))}")
            print(f"  [운영 흑자(상환여력>0) 확률]: {np.mean(surplus>0)*100:.1f}%")
            print(f"  [1인 실수령이 현재(응급 3,000만) 이상일 확률]: "
                  f"{np.mean(net/2 >= 0.30)*100:.1f}%")


# ---------------------------------------------------------------
# 4. 민감도: 무엇이 결과를 가장 크게 흔드는가
# ---------------------------------------------------------------
def sensitivity_section():
    print("\n" + "=" * 72)
    print("[4] 민감도 (기준: 의사 10명 x 일 25명 x 객단가 14만 = 월 9.8억, 고정비 70억)")
    print("=" * 72)
    base_rev = 10 * 25 * 14 * WORK_DAYS / 10000
    base_surplus = mso_annual_surplus(base_rev, 70.0)
    base_exit = DEBT / base_surplus if base_surplus > 0 else float("inf")
    print(f"  기준: 월 {base_rev:.2f}억 → 연 상환여력 {base_surplus:+.1f}억 → "
          f"완제 {base_exit:.1f}년, 부부 실수령 {FMT_MAN(couple_net_monthly(base_rev))}")

    tests = [
        ("의사당 일환자 25→28명", 10 * 28 * 14 * WORK_DAYS / 10000, 70.0, 0.30),
        ("의사당 일환자 25→22명", 10 * 22 * 14 * WORK_DAYS / 10000, 70.0, 0.30),
        ("객단가 14→15만", 10 * 25 * 15 * WORK_DAYS / 10000, 70.0, 0.30),
        ("객단가 14→12만", 10 * 25 * 12 * WORK_DAYS / 10000, 70.0, 0.30),
        ("고정비 70→64억 (램프업 채용)", base_rev, 64.0, 0.30),
        ("고정비 70→75억 (급여 인플레)", base_rev, 75.0, 0.30),
        ("변동비 30→27%", base_rev, 70.0, 0.27),
        ("의사 10→9명 (환자 동일 못받음)", 9 * 25 * 14 * WORK_DAYS / 10000, 70.0, 0.30),
    ]
    print(f"\n  {'변수':<28} | {'월매출':>7} | {'연 상환여력':>9} | {'완제소요':>8} | {'부부실수령':>9}")
    print("  " + "-" * 78)
    for name, rev, fx, vr in tests:
        s = mso_annual_surplus(rev, fx, vr)
        e = f"{DEBT/s:>6.1f}년" if s > 0 else "    불가"
        print(f"  {name:<26} | {rev:>6.2f}억 | {s:>+9.1f}억 | {e} | {FMT_MAN(couple_net_monthly(rev)):>9}")


if __name__ == "__main__":
    deterministic_section()
    capacity_grid_section()
    mc_section()
    sensitivity_section()
