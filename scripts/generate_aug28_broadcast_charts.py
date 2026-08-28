#!/usr/bin/env python3
"""8월 28일 방송 코멘트 교차 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT_DIR = Path("/workspace/reports/charts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GRAY = "#4B5563"
GREEN = "#166534"
RED = "#991B1B"
ORANGE = "#C2410C"
LIGHT = "#EEF2F8"
OK_BG = "#E8F5E9"
BAD_BG = "#FDECEA"
WARN_BG = "#FFF8E7"
BLUE_BG = "#E8F1FB"
PURPLE_BG = "#F3E8FF"


def _font():
    path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    fm.fontManager.addfont(path)
    name = fm.FontProperties(fname=path).get_name()
    plt.rcParams.update(
        {
            "font.family": name,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "text.color": NAVY,
        }
    )
    return name


def _save(fig, name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.18)
    plt.close(fig)
    print(path)


def _esc(text: str) -> str:
    return text.replace("$", r"\$") if text else text


def _box(ax, x, y, w, h, title, body, fc=LIGHT, ec="#D0D7E2", title_c=NAVY, fs=10.0, bfs=8.0):
    title = _esc(title)
    body = _esc(body)
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.05,
            edgecolor=ec,
            facecolor=fc,
        )
    )
    ax.text(x + 0.12, y + h - 0.14, title, fontsize=fs, fontweight="bold", color=title_c, va="top")
    if body:
        ax.text(x + 0.12, y + h - 0.46, body, fontsize=bfs, color=GRAY, va="top", linespacing=1.32)


def chart_show_map():
    _font()
    fig, ax = plt.subplots(figsize=(12.4, 6.4), dpi=170)
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.text(0.2, 6.12, "8/28 방송 시간 동기화 (ASR 기준 · 발음은 교정)", fontsize=14.5, fontweight="bold")
    ax.text(0.2, 5.78, "같은 날 같은 이벤트(한은·엔비디아·잭슨홀)를 채널마다 다른 렌즈로 본 기록", fontsize=9.2, color=GRAY)

    shows = [
        (0.2, 3.95, 3.9, 1.55, "KBS 1라디오", "윤지호 × 알상무\n금리·환율·엔캐리·금융주\n한은 종점 3.50 / 원달러 1280", OK_BG, "#86C99A"),
        (4.25, 3.95, 3.9, 1.55, "채슬리 박세익", "잭슨홀 트라우마·반도체 가격\n삼전 <25만 착가 / 닉스 매물벽\n할로윈 전략 · 9월 역발상", WARN_BG, GOLD),
        (8.3, 3.95, 3.9, 1.55, "대신 문남중", "엔비디아 +70% = 공급 부족\n연준은 인하 기대 / 한은은 성장\n원달러 1400 전후", BLUE_BG, NAVY2),
        (0.2, 2.15, 3.9, 1.55, "아신 이영수", "메모리 선주문 +1,600억$\n4나노 풀가동 vs 2나노\n닉스 6 / 삼전 4 분할", PURPLE_BG, "#6B21A8"),
        (4.25, 2.15, 3.9, 1.55, "케스닥·딥담화", "김장현·이진호·이건희\n6,400~7,000 박스\nAI 익스포저 확대·순환매", LIGHT, "#9AA7BD"),
        (8.3, 2.15, 3.9, 1.55, "IBK 박근형", "엔비디아 숏커버 → 메모리 약세\n약정 1,190→2,760억$\n비CSP +138~140%", BAD_BG, "#E8A0A0"),
    ]
    for args in shows:
        _box(ax, *args[:7], ec=args[7], fs=11.2, bfs=8.4)

    _box(
        ax,
        0.2,
        0.18,
        12.0,
        1.75,
        "한 줄 합의 vs 갈라지는 축",
        "합의: 잭슨홀은 무이벤트 · +70%는 수요 천장이 아님 · 메모리 펀더는 안 깨짐 · 9월은 지수보다 순환매.\n"
        "갈림: 한은 종점 3.50(알상무) vs ~3.25 종료(박세익) · 원달러 1280 vs 1400전후 · 반도체 비중확대 vs 가격 기다림 vs 포트 분산.",
        fc="#F7F9FC",
        ec=NAVY,
        fs=11.0,
        bfs=8.6,
    )
    _save(fig, "17_broadcast_map.png")


def chart_cross():
    _font()
    fig, ax = plt.subplots(figsize=(12.6, 7.1), dpi=170)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 7.1)
    ax.axis("off")
    ax.text(0.18, 6.82, "전문가 교차표 · 같은 질문에 다른 답", fontsize=14.5, fontweight="bold")

    cols = ["이슈", "알상무", "박세익", "문남중", "이영수", "케스닥", "박근형"]
    rows = [
        ["한은 종점", "3.50\n연내+연초", "~3.25\n끝", "성장 때문\n올해 추가 어려움", "미금리가 본진", "영향 작다", "지수엔 제한"],
        ["연준 9월", "침묵=독립\n연말 재편", "동결\n인하 말 없음", "올해 동결\n내년 상반 인하 2번", "인상=패권 악수", "워시 침묵", "연설 경계"],
        ["원달러", "더 하락\n마음속 1280", "—", "1400 전후\n일시요인", "—", "강세→수출환 부담", "—"],
        ["반도체", "싸서 산다\n업사이드 제한", "착한 가격만\n닉스 매물벽", "계속 비중확대", "눌림 분할\n6:4", "AI버킷 분산\n던지지 말 것", "펀더 OK\n수급 꼬임"],
        ["9월 장", "10월 조심\n11~12 좋다", "중순까지\n역발상 저가", "계절약세 약함\n오버웨이트", "시간 필요\n전고 트라이", "6400~7000\n7000 매물벽", "박스 트레이딩\n7400 1차"],
        ["AI 신용", "부채 20%\n삼각(구조조정)", "이벤트 약세\n이미 맞음", "순환금융 기우\n~2034", "5000억$ 플랫폼\n회수기간 짧음", "익스포저 재배치", "비CSP 성장\n순환출자 완화"],
    ]
    xs = [0.15, 1.55, 3.35, 5.15, 6.95, 8.75, 10.55]
    ws = [1.32, 1.72, 1.72, 1.72, 1.72, 1.72, 1.88]
    colors = {
        (0, 1): WARN_BG,
        (0, 2): OK_BG,
        (1, 1): LIGHT,
        (1, 2): OK_BG,
        (1, 3): OK_BG,
        (2, 1): PURPLE_BG,
        (2, 3): BLUE_BG,
        (3, 1): OK_BG,
        (3, 2): WARN_BG,
        (3, 3): OK_BG,
        (3, 4): OK_BG,
        (4, 1): WARN_BG,
        (4, 2): WARN_BG,
        (4, 3): OK_BG,
        (4, 5): BLUE_BG,
        (5, 1): BAD_BG,
        (5, 3): OK_BG,
    }
    header_y = 6.28
    for x, w, c in zip(xs, ws, cols):
        ax.add_patch(
            FancyBboxPatch(
                (x, header_y),
                w,
                0.42,
                boxstyle="round,pad=0.01,rounding_size=0.05",
                linewidth=0.7,
                edgecolor=NAVY,
                facecolor=NAVY,
            )
        )
        ax.text(x + w / 2, header_y + 0.21, c, ha="center", va="center", color="white", fontsize=9.4, fontweight="bold")

    y = 5.72
    h = 0.88
    for r, row in enumerate(rows):
        for c, (x, w) in enumerate(zip(xs, ws)):
            fc = NAVY2 if c == 0 else colors.get((r, c), "#FFFFFF")
            tc = "white" if c == 0 else NAVY
            ax.add_patch(
                FancyBboxPatch(
                    (x, y),
                    w,
                    h,
                    boxstyle="round,pad=0.01,rounding_size=0.05",
                    linewidth=0.7,
                    edgecolor="#D0D7E2",
                    facecolor=fc,
                )
            )
            ax.text(
                x + w / 2,
                y + h / 2,
                _esc(row[c]),
                ha="center",
                va="center",
                fontsize=7.5 if c else 8.4,
                color=tc,
                fontweight="bold" if c == 0 else "normal",
                linespacing=1.22,
            )
        y -= h + 0.06
    ax.text(
        0.18,
        0.18,
        "색: 초록=상대적으로 완화·비중확대 · 노랑=신중·가격대기 · 빨강=리스크 강조 · 보라/파랑=레벨·환율 숫자",
        fontsize=8.2,
        color=GRAY,
    )
    _save(fig, "18_broadcast_cross.png")


def chart_nvidia_sync():
    _font()
    fig, ax = plt.subplots(figsize=(12.3, 6.55), dpi=170)
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0, 6.55)
    ax.axis("off")
    ax.text(0.2, 6.22, "엔비디아 숫자 · 방송 = Quick 코멘트 PDF와 같은 장", fontsize=14.2, fontweight="bold")
    ax.text(0.2, 5.88, "채널마다 표현만 다르고 골격은 동일. +70%는 수요 100%를 공급이 자른 천장.", fontsize=9.0, color=GRAY)

    items = [
        (0.2, 3.95, 3.9, 1.7, "실적 골격", "매출 컨센 상회 · DC 91~92%\nGPM 75% 유지, 4Q 72~73%\nFCF는 빅테크 대비 양호\nDSO 45일→60일은 LTA 대가", OK_BG, "#86C99A"),
        (4.25, 3.95, 3.9, 1.7, "가이던스", "FY28 +70% (컨센 ~40% 중반)\n실제 수요 ~+100%, 메모리가 제약\n3Q 중국 DC 제외하고도 이 숫자\n1년 앞 가이던스 최초", BLUE_BG, NAVY2),
        (8.3, 3.95, 3.9, 1.7, "메모리 전가", "서버 +15% ≠ GPU ASP +15%\n마진 3~4%pt는 하이닉스·삼전·마이크론\n선주문 1200→+1600억$ (이영수)\n약정 1190→2760억$ (박근형)", WARN_BG, GOLD),
        (0.2, 2.05, 3.9, 1.7, "수요 믹스", "하이퍼스케일러 +100%대\n비CSP(네오클라우드·주권AI\n·엔터프라이즈) +138~140%\n믹스 45.3%까지 확대 = 스윙", PURPLE_BG, "#6B21A8"),
        (4.25, 2.05, 3.9, 1.7, "왜 주가는 안 가나", "미국은 GPU·네트워크 랠리\n메모리는 숏커버 자금 이동\n2030/마진 역산(85→60)이 멀티플 캡\n한국은 선택지가 메모리에 몰림", BAD_BG, "#E8A0A0"),
        (8.3, 2.05, 3.9, 1.7, "Quick과 일치", "525조 = NVDA 315 + HBM 81\n+ 잔여 130. Top5만으론 폭등 난망\n스윙은 Neo/Sovereign/Enterprise\n마벨 AH -6% ≠ 펀더 붕괴", LIGHT, "#9AA7BD"),
    ]
    for a in items:
        _box(ax, *a[:7], ec=a[7], fs=11.0, bfs=8.2)

    _box(
        ax,
        0.2,
        0.16,
        11.9,
        1.68,
        "UBS·마이크론이 방송에서 다시 나온 이유",
        "박근형: 내년 CSP 캡엑스 중 메모리 BOM 68%. 현물 DDR4/DDR5는 안 빠짐.\n"
        "김장현: 마이크론 CEO '과거 사이클 최고 분기 마진(60%초)보다 바닥이 높다' → 증권가는 거꾸로 -20%pt를 대입해 27 PER 6배→7.5~8배로 읽음.\n"
        "그래서 펀더는 좋은데 주가는 한 번에 못 간다. 이게 8/28 공통 진단.",
        fc="#F7F9FC",
        ec=NAVY,
        fs=10.6,
        bfs=8.3,
    )
    _save(fig, "19_broadcast_nvidia.png")


def chart_september():
    _font()
    fig, ax = plt.subplots(figsize=(12.3, 6.2), dpi=170)
    ax.set_xlim(0, 12.3)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.text(0.2, 5.88, "9~12월 캘린더 · 방송이 겹치는 구간", fontsize=14.2, fontweight="bold")

    _box(ax, 0.2, 4.05, 2.85, 1.55, "지금~9월 중순", "워시 연설 무이벤트\n미국 회계연도 마감\n북클로징 · 외인 유입 약\n코스피 7,000 매물벽", WARN_BG, GOLD, fs=10.8, bfs=8.3)
    _box(ax, 3.2, 4.05, 2.85, 1.55, "9월 16일 FOMC", "컨센은 동결\n인하 발언은 기대 낮음\n한은은 이달 금통위 없음\n선제 인상 이미 씀", BLUE_BG, NAVY2, fs=10.8, bfs=8.3)
    _box(ax, 6.2, 4.05, 2.85, 1.55, "10월", "알상무: 조심\n할로윈·닉스 실적\n외인 헤지펀드 유입 창\n문남중: 정책 모멘텀", BAD_BG, "#E8A0A0", fs=10.8, bfs=8.3)
    _box(ax, 9.2, 4.05, 2.85, 1.55, "11~12월", "알상무: 좋다\n중간선거 후 연준 나설 여지\n저점 6,400~6,200\n전고 트라이는 연말~1H", OK_BG, "#86C99A", fs=10.8, bfs=8.3)

    _box(
        ax,
        0.2,
        0.2,
        11.9,
        3.6,
        "실전으로 옮기면 (방송 합의 · 매수/매도 권유 아님)",
        "1. 반도체: 펀더 붕괴가 아니라 수급·멀티플 캡. 본전되면 판다는 2021 스크립트 반복 경고(박세익).\n"
        "2. 가격: 박세익 삼전 25만 이하 착가 / 30만·닉스 250만 이상은 기다림. 이영수 닉스6:삼전4 눌림 분할.\n"
        "3. 순환: 변압기·2차전지·DC/건설·화장품·금융(증권). 예쁜 차트 추격 금지. 스토리+3년 적자 회피.\n"
        "4. 포트: 김장현 AI / 비AI / 현금 ~33. Quick 07:54는 AI~50 · 비AI 20~30 · 현금 20~30.\n"
        "5. 레벨: 단기 하단 6,400 부근에서 선물 받침. 7,000은 개인 매물. 1차 저항 7,400~7,500. 8,000~8,500은 두꺼운 벽.\n"
        "6. 매크로: 잭슨홀 침묵이 호재. 한은 종점 논쟁은 주식보다 채권·금융주에 더 중요.",
        fc="#F7F9FC",
        ec=NAVY,
        fs=11.0,
        bfs=8.55,
    )
    _save(fig, "20_broadcast_sept.png")


def chart_asr():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.8), dpi=170)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")
    ax.text(0.2, 5.48, "ASR 교정표 · 대본을 읽을 때", fontsize=14.2, fontweight="bold")
    pairs = [
        ("케빈 워씨 / 케빈너시 / 케비너시", "Kevin Warsh 연준 의장"),
        ("베센트 / 배센트", "Scott Bessent 재무장관"),
        ("EB / 22B", "ECB"),
        ("신혼성 총재", "한은 총재 (유럽·BIS 경력으로 소개)"),
        ("엔비대아 / M비DI / HBN", "NVIDIA / HBM"),
        ("창신 / 양 메모리", "CXMT / YMTC"),
        ("4난노 / 2노 / 네비오스", "4nm / 2nm / Nebius"),
        ("콧방귀 · [웃음] · 자막 잡음", "내용 아님 · 무시"),
    ]
    y = 4.38
    for i, (a, b) in enumerate(pairs):
        x = 0.2 if i % 2 == 0 else 6.25
        if i % 2 == 0 and i:
            y -= 1.05
        _box(ax, x, y, 5.75, 0.92, a, b, fc=LIGHT if i % 2 == 0 else BLUE_BG, fs=10.0, bfs=8.4)
    _save(fig, "21_broadcast_asr.png")


def main():
    chart_show_map()
    chart_cross()
    chart_nvidia_sync()
    chart_september()
    chart_asr()


if __name__ == "__main__":
    main()
