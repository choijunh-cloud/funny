#!/usr/bin/env python3
"""인사이트 마크다운 정리. 숫자는 insights_data와 동일 소스."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import insights_data as D

OUT = Path("/workspace/reports/2026-09-20-study-insights.md")


def write() -> Path:
    theses = "\n".join(
        f"| {t['id']} | **{t['title']}** | {t['line']} | {t['watch']} |"
        for t in D.THESES
    )
    checks = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in D.CHECKPOINTS)
    h2 = "\n".join(
        f"| {i} | {n} | {pw:.1f}% | {w:.1f}% | {act} |"
        for i, (n, pw, w, act) in enumerate(D.H2_TOP10, 1)
    )
    unlock = "\n".join(f"- {x}" for x in D.DO_NOT_LOCK)
    corpus = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in D.CORPUS)
    evo = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in D.EVOLUTION)
    text = f"""# 8월–9월 투자 스터디 인사이트

기준일 2026-09-20. 출처는 funny 저장소 강의·브리프·하이브리드 모델.
로컬 워커는 없어 클라우드 저장소에 있는 투자 스터디만 읽었다.
커넥톰·봉직·클리닉·톤즈는 제외.

숫자·시나리오는 공개 코멘트·강의 스냅샷이다. 실시간 시세나 매수 추천이 아니다.

## 오늘 한 장으로 보면

공통 분모는 AI CAPEX다. 수요를 정확히 예측할 수 없으니 모델·데이터센터·GPU에 기대고, 자금이 빠듯하니 서로 묶는다.

- 장비는 **수주**
- SK는 **할인율**
- Atlas는 **공장 배치**
- 9월 추가 축: 약한 고리 = **자금 + 장기금리**

사이렌(10Y 5% 안착 · oil 120)은 미발화. 9/18 장중 10Y {D.TENY_FRI_PRINT}는 터치이지 안착이 아니다.

## 여덟 테제

| ID | 제목 | 한 줄 | 확인 |
|----|------|-------|------|
{theses}

## 읽은 세션

| 날짜 | 제목 | 내용 | 구분 |
|------|------|------|------|
{corpus}

## 관점 진화

| 시기 | 초점 | 한 줄 |
|------|------|-------|
{evo}

## 준혁 프레임 (덮어쓰지 않음)

| 프레임 | 선 | 최근 관측 |
|--------|----|-----------|
| 10Y | {D.TENY_FRAME:.2f}% | 워킹 {D.TENY_WORKING_LO}–{D.TENY_WORKING_HI} · 장중 {D.TENY_FRI_PRINT} |
| 30Y | {D.THIRTY_Y_FRAME:.1f}% | 9/15 낙찰 5.308% |
| TIPS | {D.TIPS_FRAME:.1f}% | 8/21 근처 2.94% |
| Oil | {D.OIL_SIREN:.0f} | WTI {D.FRI_WTI} · Brent {D.FRI_BRENT} |
| 환원 | 닉스 자사주 vs 삼성 배당/1월 | 스타일 분리 |

Gravity AND: 10–20Y가 {D.GRAVITY_LO}–{D.GRAVITY_HI}%를 추세로 돌파 **그리고** No Way Back. 9/18 종가 쪽은 4.951 근처, AND 미충족.

## 9/18 테이프 (잠근 숫자)

- KOSPI {D.KOSPI_SEP18:,.2f} (+{D.KOSPI_SEP18_PCT}%)
- 삼성 {D.SAMSUNG_SEP18:,} (+{D.SAMSUNG_SEP18_PCT}%)
- 하이닉스 {D.HYNIX_SEP18:,} (+{D.HYNIX_SEP18_PCT}%)
- SOX +{D.FRI_SOX_PCT}% · Nasdaq +{D.FRI_NASDAQ_PCT}%
- FOMC {D.FED_BAND} (+{D.FED_HIKE_BP}bp) · 점도표 {D.DOT_MEDIAN}
- BOJ {D.BOJ_RATE}% · USD/JPY {D.USDJPY_SEP18} · 원/달러 {D.USDKRW_SEP18}

박스 6,000–7,150. 고점 {D.KOSPI_PEAK:,.2f} 대비 9/18은 {D.kospi_drawdown_from_peak():.1f}%.

## 메모리 · 토큰 · 인프라

- 8/18 PER: 닉스 {D.AUG18_PER['hynix_26']}/{D.AUG18_PER['hynix_27']}배, 삼전 {D.AUG18_PER['samsung_26']}/{D.AUG18_PER['samsung_27']}배
- 9/15 PER: 닉스 27E {D.SEP15_PER['hynix_27']}배, 삼전 {D.SEP15_PER['samsung_27']}배, MU {D.SEP15_PER['mu_cy27']}배
- Citi DRAM 수요 {D.CITI_DRAM_DEMAND[0]}/{D.CITI_DRAM_DEMAND[1]} vs 공급 {D.CITI_DRAM_SUPPLY[0]}/{D.CITI_DRAM_SUPPLY[1]}
- 토큰 8월: 볼륨 MoM +{D.TOKEN_VOL_MOM}% · 단가 MoM {D.TOKEN_PRICE_MOM}%
- NVDA Q2: 매출 ${D.NVDA_REV}B · OCF/NI {D.NVDA_OCF_NI}% · 공급약정 ${D.NVDA_SUPPLY_COMMIT}B
- Dell 백로그 ${D.DELL_BACKLOG}B · Oracle RPO ${D.ORCL_RPO}B
- DC 갭 {D.dc_gap()} GW (수요 {D.DC_2030_DEMAND} − 그리드 {D.DC_2030_GRID})

저PER을 싸다고 읽지 말 것. 강의 산식 밴드(닉스 175–242만, 삼전 28.7–33.5만)와 IB/게스트 가격을 섞지 말 것.

## 소부장 · SK · Atlas

| 이름 | 핵심 | 확인 |
|------|------|------|
| 테스 | 수주 2,823억 QoQ 2배 | BSD DRAM/HBM 퀄 |
| 한미 | OPM {D.HANMI_OPM}% | 점유율 {D.HANMI_SHARE[0]}–{D.HANMI_SHARE[1]}% vs 한화세미텍 |
| 원익 | 잔고 ~4,000억 | 3Q OP · 4Q 레버리지 · 2027 수주 |
| SK에코 | 표 {D.SK_ECO_TABLE}조 vs 잔고 {D.SK_ECO_BACKLOG}조 | 재평가 시 TP {D.SK_REVAL_TP[0]}–{D.SK_REVAL_TP[1]}만도 산출 |
| Atlas | Fleet × 가동률 × 데이터 | 11월 모비스 시제품 · 2028 HMGMA |

## H2 Top 10 (9/3 계산)

주식 {D.H2_EQUITY}% / 현금·채권 {D.H2_CASH}%. as-of KOSPI {D.H2_ASOF_KOSPI}.

| # | 종목 | PW | 기존 비중 | 액션 |
|---|------|----|-----------|------|
{h2}

신규자금: 한국금융지주 > NAVER > 모비스 > 한전. 10월 전 삼전닉스 추가 없음.

Book C: SEMI {D.BOOK_C[0][1]} / SHORT_DURATION {D.BOOK_C[1][1]} / OIL_DOWN {D.BOOK_C[2][1]} / HEDGE {D.BOOK_C[3][1]}.

## 확인 캘린더

| 때 | 항목 | 축 |
|----|------|----|
{checks}

## 잠그지 않는다

{unlock}

## 가져갈 세 문장

1. 소부장: 2Q 숫자보다 수주가 매출로 바뀌는 하반기, 그리고 2027 수주가 다시 증가하는지가 승부처다.
2. SK: 할인율이 좁혀질 이유가 늘었다. 그래도 기본은 하이닉스와 이노베이션이다.
3. 상단: 하이퍼스케일러 현금이 데이터센터나 토큰으로 다시 도느냐. 답이 나오면 박스가 열린다.

시각화 보드: `lectures/8월-9월 투자 스터디 인사이트 한장.html` (차트 26장).
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(write())
