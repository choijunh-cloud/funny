#!/usr/bin/env python3
"""8월 25일 게시용 문안(.docx) 생성."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from notes_style import GOLD, GRAY, NAVY, NAVY2, Notes

CHARTS = Path("/workspace/lectures/charts")
OUT_PATH = Path("/workspace/lectures/8월 25일 게시용 문안.docx")


def build():
    n = Notes(
        header="2026.8.25 게시용 문안  ·  제공 PDF + 방송 프레임 + 8/24 교정",
        footer="[확인] 보도·원문  ·  [방송] 출연자 발언  ·  [가정] 시나리오  ·  [역산] 계산  ·  매수·매도 추천 아님  ·  ",
        title="8월 25일 게시용 문안",
        subject="금리, 베선트 풋, 금융억압, AI 전가, 한국 수급, 로봇",
    )

    n.p("POSTING COPY  ·  2026. 8. 25", size=10.5, color=GRAY, align="center", space_after=4)
    n.p("게시용 문안", size=13, bold=True, color=GOLD, align="center", space_after=2)
    n.p("금리는 풋의 테스트다", size=22, bold=True, color=NAVY, align="center", space_after=2)
    n.p("제공 PDF 도표 + 8/24 여섯 교정 유지", size=13, bold=True, color=NAVY2, align="center", space_after=8)

    n.callout(
        "이 문서의 쓰임",
        [
            "배포용이다. 상세 레포트의 방향은 유지하되, 분모·일정·PDF 실행판을 같이 붙였다.",
            "원본 PDF: lectures/sources/20260825_market_strategy_report_korean_font_fixed.pdf",
            "바이백 창은 재무부 발표 9/9~11/4 [확인]. PDF는 첫 확대 매입을 9/10으로 표기. NVIDIA 공식 콜은 8/27 06:00 KST [확인].",
        ],
        kind="key",
    )
    n.image(CHARTS / "20260825_source_legend.png", 16.2, "그림. 숫자 태그.")

    n.h1("한 줄", num="1.")
    n.callout(
        "게시 문안",
        [
            "시장이 지치는 이유는 장기금리다. 다만 미국 10년 4.7%는 이미 할인 구간이다. ‘5%면 S&P −20%’만으로 추가 충격이 오지는 않는다.",
            "8월 24일은 금리·유가가 빠졌는데 반도체가 급락했다. 초점은 NVIDIA 실적, AI CAPEX 기대, 데이터센터 정치 리스크로 이동했다.",
            "오는 경우는 베선트 풋이 임계를 못 막을 때다. 금융억압은 수년 시계의 스케치지, 이번 주 매수 이유가 아니다.",
        ],
        kind="bull",
    )

    n.h1("반드시 유지할 여섯 교정", num="2.")
    n.table(
        ["항목", "고쳐 쓸 말"],
        [
            ["마이크론 150%", "데이터센터 요구량 ÷ 확약 가능 공급량. 산업 전체 50% 부족이 아님"],
            ["MCP · HBM · DDR5", "패키지·통관 ≠ 제품 ≠ 세대 규격"],
            ["NVIDIA 15%", "AI 칩 탑재 서버 시스템 가격. 공식 GPU ASP 아님"],
            ["29.45% · 25.94%", "미국 상업성·광고 유발 표본. 전체 검색·대화 아님"],
            ["OpenAI $3~$5", "권장 최대 CPC 입찰가. 실제 CPC 아님"],
            ["에스피지 SDD", "중국 제품 무게의 약 90% = 약 10% 경량화. 5,000대는 목표"],
        ],
        col_widths=[4.4, 13.2],
    )
    n.callout(
        "쓰지 말 것",
        "트럼프가 Apple의 CXMT·YMTC 구매를 승인할 예정이다. 웨이보발 루머(Wccftech 60% Plausible).",
        kind="bear",
    )

    n.h1("금리 — 10년 5%와 30년 5%는 다르다", num="3.")
    n.image(CHARTS / "20260825_pdf_fig01_rate_map.png", 16.2, "그림. 10년은 스트레스 구간, 30년은 이미 5% 위. [PDF]")
    n.callout(
        "게시 문안",
        [
            "10년 5%는 자동 폭락선이 아니다. MRB 15–20%는 5% 접근 + 추세 미꺾임 + 정책 실패가 겹칠 때의 조건부 시나리오다.",
            "30년은 이미 5% 위(8/24 종가 5.228%). Hartnett의 ‘5% 밑’은 깨져 있다. 폭락이 없었으니 트리거가 아니라 풋이 먹히느냐의 테스트다.",
            "준혁 본선: 10년 5%(4.9% 이하 할인) / 30년 6% / TIPS 3.0%. PDF 강한 위험선은 30년 5.40%.",
        ],
        kind="bull",
    )
    n.image(CHARTS / "20260825_pdf_fig02_aug24_market.png", 16.2, "그림. 금리·유가 하락에도 반도체 매도가 집중됐다. [PDF]")

    n.h1("베선트 풋 ≠ QE", num="4.")
    n.image(CHARTS / "20260825_bessent_vs_qe.png", 16.2, "그림. 누가 사나, 재원, 대차가 다르다.")
    n.callout(
        "게시 문안",
        [
            "회당 $2B → 최소 $4B. 재무부 발표 9/9~11/4. [확인] 제공 PDF는 첫 확대 매입을 9/10로 표기.",
            "재원 TGA 약 $9,400억~$1T. 전액 투입 여유자금이 아니다. 아직 한 장도 안 샀다. [방송]",
            "성공: 30년 5.0% 아래, 10년 4.9% 아래, 경매 tail 축소, 달러·금 안정.",
            "실패: 30년 5.3–5.4% 재상승, 10년 5% 접근, 금리↑·달러↓·금↑.",
        ],
        kind="bull",
    )

    n.h1("정치 2×2 — 사람을 응원하지 않는다", num="5.")
    n.image(CHARTS / "20260825_politics_2x2.png", 16.2, "그림. 규제 완화 + 적자·관세면 실적은 좋아도 밸류가 꺾인다. [PDF]")
    n.callout(
        "게시 문안",
        [
            "AI 규제 완화 + 재정 안정은 실적·밸류 모두 긍정이다.",
            "규제 완화 + 적자·관세 인플레는 실적은 좋아도 장기금리로 밸류가 부정이다.",
            "텍사스 DC는 단기 인허가·전력 지연과 장기 Dark GPU 억제를 같이 본다. 규제가 곧 총수요 파괴는 아니다.",
        ],
        kind="bull",
    )

    n.h1("이번 주", num="6.")
    n.image(CHARTS / "20260825_pdf_fig05_timeline.png", 16.2, "그림. 실물수요 → 물가 → 정책반응. [PDF]")
    n.table(
        ["때", "이벤트", "보면"],
        [
            ["8/26 21:30", "7월 PCE (+GDP 수정)", "코어 3.3 부합 vs 3.4 이상"],
            ["8/27 06:00", "NVIDIA 공식 콜", "3Q 가이드 ~$103B, 마진 75%"],
            ["8/27", "금통위", "원화·국내 채권"],
            ["8/28 23:00", "워시 잭슨홀", "장기금리 신뢰"],
            ["9/9~", "바이백 실행", "발표가 아니라 실행. PDF는 9/10"],
        ],
        col_widths=[3.4, 5.6, 8.6],
    )
    n.callout(
        "게시 문안 [가정]",
        [
            "기본: 부합 + 원론 → 코스피 7,000~7,200.",
            "최악: 가이드 미달 + 코어 상회 + 매파 → 30년 5.4%, 코스피 6,000.",
        ],
        kind="note",
    )
    n.image(CHARTS / "20260825_pdf_fig06_2x2.png", 16.2, "그림. PCE × NVIDIA. 워시는 강도를 조절한다. [PDF]")

    n.h1("AI — 수요는 실물, 약한 고리는 조달", num="7.")
    n.callout(
        "게시 문안",
        [
            "수요는 아직 실물이다. 약한 고리는 조달(OpenAI·소프트뱅크·PF)과 건설 병목, 모델 가격을 못 올리는 구조다.",
            "SoftBank 1조엔 개인채·OpenAI 커밋 $60B+는 레버리지가 열려 있음을 보여 준다. [확인]",
            "랩 $2T·ARR 둔화·중국 모델 33%는 수요 사망이 아니라 가격결정력 약화다. 전가가 소비자 Q를 죽이면 그때가 수요 문제다.",
        ],
        kind="bull",
    )
    n.image(CHARTS / "20260825_pdf_fig07_capital.png", 16.2, "그림. SoftBank → OpenAI → DC → GPU/HBM. [PDF]")

    n.h1("한국 — 닉스가 먼저, 삼성은 규모", num="8.")
    n.image(CHARTS / "20260825_pdf_fig08_return.png", 16.2, "그림. 명목 규모와 주당효과는 다르다. [PDF]")
    n.callout(
        "게시 문안",
        [
            "수급·주당효과는 닉스(40조 전량소각). 명목 규모·분산은 삼성(90~110조, 3Q 배당 30조).",
            "7월 초과 낙폭은 영국 헤지 디레버리지로 읽힌다. 미국 장기자금은 샀다. [방송]",
            "ABF는 필름 절대 부족보다 고사양 기판 수율·유효 CAPA. SKT·네이버는 발표 CAPA가 아니라 가동·이용률·외부 매출을 본다.",
        ],
        kind="bull",
    )
    n.image(CHARTS / "20260825_pdf_fig09_abf.png", 16.2, "그림. ABF는 유효 CAPA. [PDF]")

    n.h1("실행 — 고점은 본전이 아니다", num="9.")
    n.callout(
        "게시 문안 [PDF]",
        [
            "과거의 고점은 본전이 아니다. 매도 기준은 투자논리의 유효성이다.",
            "가장 위험한 조합: 코어 PCE 3.4%+ · NVIDIA 가이드 미달 · 30년 5.4%+ · 워시 신뢰 실패 · 텍사스형 규제 확산. 세 가지 이상이 동시에 올 때 체제가 바뀐다.",
            "이벤트 전에는 현금을 보유한 바벨. PCE·NVIDIA 확인 전 무리한 방향성 베팅을 피한다.",
        ],
        kind="bull",
    )
    n.table(
        ["상태", "AI·반도체", "Non-AI", "현금·헤지"],
        [
            ["이벤트 전", "25–30%", "30–35%", "35–45%"],
            ["우호 확인", "35–45%", "30–35%", "20–30%"],
            ["최악 조합", "15–25%", "25–35%", "40–55%"],
        ],
        col_widths=[4.4, 4.4, 4.4, 4.4],
    )
    n.p("위 비중은 개인 권고가 아니라 제공 PDF를 구조화한 조건부 템플릿이다.", size=10, color=GRAY)

    n.h1("한 장으로 올리는 결론", num="10.")
    n.callout(
        "게시 문안",
        [
            "아직은 전면적 위험회피보다 현금을 보유한 바벨이 적절하다.",
            "PCE와 NVIDIA를 확인하기 전에 무리한 방향성 베팅을 피하고, 우호적 조합이면 실적과 현금흐름이 검증된 AI 대형주와 인프라를 분할 확대한다.",
            "핵심은 150% 헤드라인보다 계약, MCP 수출액보다 kg당 통관단가, 목표주가보다 출하·수율, 광고 노출률보다 CTR·실효 CPC다.",
        ],
        kind="key",
    )
    n.p("매수·매도 추천이 아니다. 작성 기준 2026-08-25.", size=10, color=GRAY)

    n.save(OUT_PATH)
    print(OUT_PATH)


if __name__ == "__main__":
    build()
