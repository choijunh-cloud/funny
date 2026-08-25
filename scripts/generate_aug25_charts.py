#!/usr/bin/env python3
"""8월 25일 상세 통합 레포트 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT_DIR = Path("/workspace/lectures/charts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GRAY = "#4B5563"
GREEN = "#166534"
RED = "#991B1B"
TEAL = "#0F766E"
LIGHT = "#EEF2F8"


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


def _box(ax, x, y, w, h, title, body, fc=LIGHT, ec="#D0D7E2"):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.03,rounding_size=0.08",
            linewidth=1.0, edgecolor=ec, facecolor=fc,
        )
    )
    ax.text(x + 0.12, y + h - 0.18, title, fontsize=10.5, fontweight="bold", color=NAVY, va="top")
    ax.text(x + 0.12, y + h - 0.55, body, fontsize=8.6, color=GRAY, va="top", linespacing=1.35)


def week_branch():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=180)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("이번 주 분기  ·  8/26~28", fontsize=15, color=NAVY, loc="left", pad=8)

    items = [
        (0.2, 6.6, "8/26 21:30  7월 PCE", "가정 YoY +3.6% · 코어 +3.3%\n코어 3.4% 이상이면 9월 인상 확률 40%대 [가정]"),
        (5.15, 6.6, "8/27 06:00  엔비디아 FY27 2Q", "공식 콜 06:00 KST [확인]\n컨센 약 919억(+97%). 3Q 가이드 ~1,030억 · 마진 75%"),
        (0.2, 3.4, "8/27  금통위", "인상 vs 동결 갈림\n국내 채권 · 환율"),
        (5.15, 3.4, "8/28 23:00  워시 잭슨홀", "취임 후 첫 연설 · 포워드가이던스 폐지\n스티펠은 원론 예상"),
    ]
    for x, y, t, b in items:
        _box(ax, x, y, 4.65, 2.7, t, b)

    _box(
        ax, 0.2, 0.25, 4.65, 2.7,
        "기본 [가정]",
        "엔비디아 부합 + PCE 예상 + 워시 원론\n→ 코스피 7,000 안착 ~ 7,200(20주선)",
        fc="#E8F5E9", ec="#86EFAC",
    )
    _box(
        ax, 5.15, 0.25, 4.65, 2.7,
        "최악 [가정]",
        "가이드 미달 + 코어 상회 + 워시 매파\n→ 30년 5.4%, 코스피 6,000 지지 테스트",
        fc="#FDECEA", ec="#FCA5A5",
    )
    out = OUT_DIR / "20260825_week_branch.png"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def bessent_vs_qe():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 5.4), dpi=180)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_title("베선트 풋은 QE가 아니다", fontsize=15, color=NAVY, loc="left")

    rows = [
        ("누가 사나", "재무부 (TGA 현금)", "연준 (대차 확대)"),
        ("재원", "이미 걷어 둔 세금·현금", "준비금 창출 · 새 유동성"),
        ("대차대조표", "정부 현금 재배치", "연준 자산·부채 증가"),
        ("규모", "회당 20억→40억 달러+", "수조 달러 사이클"),
        ("원인 치유", "적자·발행·텀프리미엄 미접촉", "침체 뒤 수요 부족 대응"),
        ("다음 창", "9월 9일 실제 매입", "정책금리·대차 경로"),
    ]
    ax.text(3.4, 8.55, "베선트 풋", fontsize=12, fontweight="bold", color=NAVY2, ha="center")
    ax.text(7.3, 8.55, "QE", fontsize=12, fontweight="bold", color=RED, ha="center")
    for i, (k, a, b) in enumerate(rows):
        y = 7.7 - i * 1.15
        ax.add_patch(FancyBboxPatch((0.2, y), 2.4, 1.0, boxstyle="round,pad=0.02,rounding_size=0.06", fc=NAVY, ec=NAVY))
        ax.add_patch(FancyBboxPatch((2.8, y), 3.3, 1.0, boxstyle="round,pad=0.02,rounding_size=0.06", fc="#E8F1FB", ec="#BFDBFE"))
        ax.add_patch(FancyBboxPatch((6.3, y), 3.5, 1.0, boxstyle="round,pad=0.02,rounding_size=0.06", fc="#FDECEA", ec="#FECACA"))
        ax.text(1.4, y + 0.5, k, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.text(4.45, y + 0.5, a, ha="center", va="center", color=NAVY, fontsize=9.2)
        ax.text(8.05, y + 0.5, b, ha="center", va="center", color=RED, fontsize=9.2)
    out = OUT_DIR / "20260825_bessent_vs_qe.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def repression_map():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.3), dpi=180)

    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("세 선택지 — 왜 억압인가", fontsize=13, color=NAVY)
    choices = [
        (0.4, 6.6, "긴축", "정의로워 보인다.\n선진국에서 성공 사례 드묾.\n한국 IMF, 프랑스 총리 교체.", "#FFF8E7"),
        (0.4, 3.5, "디폴트", "힘없는 나라의 선택.\n기축국은 발권력이 있다.\n선택 이유 거의 제로.", "#FDECEA"),
        (0.4, 0.4, "금융억압 + 인플레", "명목금리 고정 → 실질금리 −.\n불만은 나와도 봉기는 작다.\n역사의 본능적 경로.", "#E8F5E9"),
    ]
    for x, y, t, b, fc in choices:
        _box(ax, x, y, 9.2, 2.8, t, b, fc=fc)

    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("누가 이기고 지는가", fontsize=13, color=NAVY)
    _box(ax, 0.3, 5.2, 9.4, 4.3, "유리", "고정금리 채무자\n실물(부동산·금·농)\n가격결정력 있는 기업 (P를 올리는 국면)", fc="#E8F5E9")
    _box(ax, 0.3, 0.4, 9.4, 4.3, "불리", "현금·예금 (1~2% vs 물가 10%+)\n임금 근로자\n채권 투자자 · 대부분 개인", fc="#FDECEA")

    fig.suptitle("금융억압은 수년 시계의 스케치이지, 이번 주 매수 이유가 아니다", fontsize=12.5, color=NAVY, y=1.02)
    out = OUT_DIR / "20260825_repression_map.png"
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def korea_return():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 5.2), dpi=180)
    labels = ["확정 집행", "소각 여부", "속도 가시성", "거래대금 충격"]
    # qualitative scores 1-5 for visual only
    hynix = [5, 5, 5, 4]
    samsung = [3, 2, 2, 3]
    x = np.arange(len(labels))
    w = 0.36
    ax.bar(x - w / 2, hynix, w, color=NAVY, label="SK하이닉스 40조 매입+전량소각", zorder=3)
    ax.bar(x + w / 2, samsung, w, color=GOLD, label="삼성 90~110조 (배당 先行)", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 6.2)
    ax.set_yticks([])
    ax.set_title("환원 1라운드 수급 — 닉스 우위 (상대 점수, 절대 규모 아님)", fontsize=13.5, color=NAVY)
    ax.legend(frameon=False, loc="upper right")
    ax.yaxis.grid(True, linestyle="--", color="#E2E8F0")
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    notes = [
        "닉스: 일 ~65만주·약 1조, 이 속도면 10월 중순 종료 [방송]",
        "삼성: 3Q 현금배당 ~30조(10월 이사회), 잔여 60~80조는 2027년 1월 [확인]",
        "임직원 자사주 15조는 별도·소각 아님. 금산법 10%가 소각을 제약 [확인/방송]",
    ]
    ax.text(0.0, -0.22, "\n".join(notes), transform=ax.transAxes, fontsize=8.3, color=GRAY)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    out = OUT_DIR / "20260825_korea_return.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def rate_thresholds():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 4.8), dpi=180)
    names = ["미국 10년", "미국 30년", "30년 TIPS"]
    now = [4.704, 5.234, 2.94]
    line = [5.0, 6.0, 3.0]
    discount = [4.9, None, None]
    x = np.arange(len(names))
    ax.bar(x - 0.18, now, 0.36, color=NAVY2, label="최근 세션 (방송)", zorder=3)
    ax.bar(x + 0.18, line, 0.36, color=GOLD, label="준혁 본선 임계", zorder=3)
    ax.axhline(4.9, color=GREEN, linestyle="--", linewidth=1.0, alpha=0.7)
    ax.text(2.35, 4.96, "10년 4.9% 이하 = 이미 할인", fontsize=8, color=GREEN)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=11)
    ax.set_ylabel("%")
    ax.set_ylim(0, 7.2)
    ax.set_title("금리 임계 — 헤드라인 5%만으로 추가 충격이 오지는 않는다", fontsize=13.5, color=NAVY)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle="--", color="#E2E8F0")
    for i, (a, b) in enumerate(zip(now, line)):
        ax.text(i - 0.18, a + 0.12, f"{a:.3f}" if i == 0 or i == 1 else f"{a:.2f}", ha="center", fontsize=8.5, color=NAVY)
        ax.text(i + 0.18, b + 0.12, f"{b:.1f}", ha="center", fontsize=8.5, color=GOLD)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.text(
        0.0, -0.18,
        "Hartnett의 '30년을 5% 밑으로'는 이미 5.2%에서 깨져 있다. 폭락이 없었으니 트리거가 아니라 풋이 먹히느냐의 테스트다.\n"
        "MRB: 10년 5% 근접 시 S&P −15~20% — 새 뉴스가 아님. 오는 경우는 베선트 풋이 임계를 못 막을 때뿐.",
        transform=ax.transAxes, fontsize=8.2, color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    out = OUT_DIR / "20260825_rate_thresholds.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def politics_2x2():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 5.6), dpi=180)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("정치 2 x 2  ·  사람을 응원하지 말고 정책 조합을 본다  [PDF]", fontsize=14, color=NAVY, loc="left")

    cells = [
        (0.25, 5.15, "AI 규제 완화 + 재정 안정", "실적 긍정\n밸류에이션 긍정", "#E8F5E9", "#86EFAC"),
        (5.1, 5.15, "AI 규제 완화 + 적자·관세 인플레", "실적은 긍정\n장기금리로 밸류는 부정", "#FFF8E7", "#FCD34D"),
        (0.25, 0.35, "AI 규제 강화 + 금리 안정", "CAPEX 둔화\n밸류는 일부 방어", "#E8F1FB", "#93C5FD"),
        (5.1, 0.35, "AI 규제 강화 + 장기금리 상승", "실적 부정\n밸류도 가장 부정", "#FDECEA", "#FCA5A5"),
    ]
    for x, y, t, b, fc, ec in cells:
        _box(ax, x, y, 4.65, 4.4, t, b, fc=fc, ec=ec)
    ax.text(
        0.25, 9.55,
        "텍사스 DC: 단기 인허가·전력 지연 vs 장기 Dark GPU·과잉 억제. 규제가 곧 총수요 파괴는 아니다.",
        fontsize=8.6, color=GRAY, va="top",
    )
    out = OUT_DIR / "20260825_politics_2x2.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def source_legend():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 3.2), dpi=180)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("숫자 태그  ·  이 레포트의 읽는 법", fontsize=14, color=NAVY, loc="left")
    items = [
        (0.2, "[확인]", "보도·원문·공시에서\n교차확인한 숫자", "#E8F5E9"),
        (2.7, "[방송]", "출연자 발언.\n방향은 쓰되 단독 근거 아님", "#E8F1FB"),
        (5.2, "[가정]", "시나리오·확률.\n기본/최악으로만 관리", "#FFF8E7"),
        (7.7, "[역산]", "공개 숫자로 계산.\n전제를 같이 적는다", "#F3E8FF"),
    ]
    for x, t, b, fc in items:
        _box(ax, x, 0.35, 2.3, 3.1, t, b, fc=fc)
    out = OUT_DIR / "20260825_source_legend.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = [
        source_legend(),
        week_branch(),
        bessent_vs_qe(),
        rate_thresholds(),
        repression_map(),
        korea_return(),
        politics_2x2(),
    ]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
