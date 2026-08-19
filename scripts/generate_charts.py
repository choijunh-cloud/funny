#!/usr/bin/env python3
"""Generate high-resolution charts for the 2026-08-19 Market Report."""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# Paths
CHARTS_DIR = Path("/workspace/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR = Path("/opt/cursor/artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Font setup
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
font_prop = fm.FontProperties(fname=FONT_PATH)
font_title = fm.FontProperties(fname=FONT_PATH, size=15, weight='bold')
font_subtitle = fm.FontProperties(fname=FONT_PATH, size=11)
font_label = fm.FontProperties(fname=FONT_PATH, size=10)
font_value = fm.FontProperties(fname=FONT_PATH, size=9.5, weight='bold')

# Styling constants
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

NAVY = "#0F2043"
NAVY_LIGHT = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#991B1B"
BLUE = "#2563EB"
GRAY = "#6B7280"
LIGHT_BG = "#F8FAFC"
CYAN = "#0EA5E9"
PURPLE = "#7C3AED"


def save_chart(fig, filename):
    p1 = CHARTS_DIR / filename
    p2 = ARTIFACTS_DIR / filename
    fig.savefig(p1, bbox_inches='tight', dpi=300)
    fig.savefig(p2, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Saved {filename}")


# -------------------------------------------------------------
# 1. Macro: US Treasury Yield vs Brent Crude vs USD/KRW
# -------------------------------------------------------------
def make_macro_chart():
    fig, ax1 = plt.subplots(figsize=(10, 5), facecolor='white')
    ax1.set_facecolor(LIGHT_BG)
    
    metrics = ['미 국채 10년물 금리', '미 국채 30년물 금리', '브렌트유 ($/배럴)', '달러-원 환율 (원)']
    
    # We will create a horizontal dashboard comparing peak vs current vs danger threshold
    categories = [
        '미 국채 10년물 (%)',
        '미 국채 30년물 (%)',
        '브렌트유 ($)',
        '달러-원 환율 (원/10)'
    ]
    
    current = [4.64, 5.19, 84.0, 141.2]
    prior_peak = [4.75, 5.34, 90.0, 152.0]
    threshold = [5.00, 5.50, 100.0, 136.0]
    
    y = np.arange(len(categories))
    height = 0.25
    
    rects1 = ax1.barh(y + height, prior_peak, height, label='단기 고점 / 전일치', color=RED, alpha=0.85)
    rects2 = ax1.barh(y, current, height, label='재무부 바이백 후 현재치', color=BLUE, alpha=0.9)
    rects3 = ax1.barh(y - height, threshold, height, label='핵심 임계선 / 위험선 (환율은 하단목표)', color=GOLD, alpha=0.85)
    
    ax1.set_yticks(y)
    ax1.set_yticklabels(categories, fontproperties=font_label)
    ax1.set_xlabel('수치 (환율은 10원 단위)', fontproperties=font_label)
    ax1.set_title('글로벌 매크로 지표 현황 및 위험 임계선 (Macro Dashboard)', fontproperties=font_title, pad=15, color=NAVY)
    ax1.legend(prop=font_label, loc='upper right')
    ax1.grid(axis='x', linestyle='--', alpha=0.5)
    
    # Add values on bars
    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            w = rect.get_width()
            val_str = f"{w:.2f}" if w < 10 else f"{w:.1f}"
            if w > 100:
                val_str = f"{int(w*10)}원"
            ax1.annotate(val_str,
                         xy=(w, rect.get_y() + rect.get_height() / 2),
                         xytext=(4, 0), textcoords="offset points",
                         ha='left', va='center', fontproperties=font_value, fontsize=8)
    
    ax1.set_xlim(0, 180)
    save_chart(fig, "macro_indicators.png")


# -------------------------------------------------------------
# 2. SK Hynix: Shareholder Return Framework (FCF 565T vs Return)
# -------------------------------------------------------------
def make_skhynix_return_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor='white')
    ax1.set_facecolor(LIGHT_BG)
    ax2.set_facecolor(LIGHT_BG)
    
    # Left: FCF vs Shareholder Return Breakdown
    categories = ['2025~27E\n누적 FCF (보수적)', '주주환원 목표\n(50% 초과)', '기확정 환원\n(자사주 소각)', '추가 환원 여력\n(배당/특별배당)']
    values = [565, 282.5, 40.0, 242.5]
    colors = [NAVY, GOLD, GREEN, BLUE]
    
    bars = ax1.bar(categories, values, color=colors, width=0.55, edgecolor='none', alpha=0.9)
    ax1.set_ylabel('금액 (조원)', fontproperties=font_label)
    ax1.set_title('SK하이닉스 2025~2027 누적 FCF 및 주주환원 배분', fontproperties=font_title, pad=12, color=NAVY)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}조원",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
    
    # Right: Base Stock vs ADR Value Comparison
    scenarios = ['현재 본주\n(150만원)', '30~35% 프리미엄\n적용 적정가', '정상 프리미엄(+20%)\n적정 본주가', '보수적 26년\nPER 6배 적용', '보수적 26년\nPER 7배 적용']
    prices = [150.0, 172.0, 190.0, 208.0, 242.0]
    bar_colors = [GRAY, BLUE, CYAN, GOLD, GREEN]
    
    bars2 = ax2.bar(scenarios, prices, color=bar_colors, width=0.55, alpha=0.9)
    ax2.set_ylabel('주가 (만원)', fontproperties=font_label)
    ax2.set_title('SK하이닉스 본주 시나리오별 적정 주가 비교', fontproperties=font_title, pad=12, color=NAVY)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    ax2.axhline(150.0, color=RED, linestyle=':', alpha=0.8, label='현재가 기준선')
    ax2.legend(prop=font_label, loc='upper left')
    
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f"{h:.0f}만원",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
    
    plt.tight_layout()
    save_chart(fig, "skhynix_return_and_valuation.png")


# -------------------------------------------------------------
# 3. Global Memory Peers PER Comparison (CY26 / CY27)
# -------------------------------------------------------------
def make_memory_valuation_chart():
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
    ax.set_facecolor(LIGHT_BG)
    
    companies = ['SK하이닉스 (본주)', '삼성전자 (본주)', 'SK하이닉스 (ADR)', '마이크론 (MU)', '샌디스크 (SNDK)']
    per_26 = [4.3, 5.2, 6.6, 7.5, 7.8]
    per_27 = [3.4, 3.7, 5.2, 6.25, 7.0] # 샌디스크 FY27 7.8
    per_conservative_27 = [5.1, 5.6, 7.7, 7.5, 8.2]
    
    x = np.arange(len(companies))
    width = 0.25
    
    r1 = ax.bar(x - width, per_26, width, label='2026E PER (배)', color=NAVY, alpha=0.9)
    r2 = ax.bar(x, per_27, width, label='2027E 컨센서스 PER (배)', color=BLUE, alpha=0.85)
    r3 = ax.bar(x + width, per_conservative_27, width, label='2027E 보수적 시나리오 PER (배)', color=GOLD, alpha=0.85)
    
    ax.set_xticks(x)
    ax.set_xticklabels(companies, fontproperties=font_label)
    ax.set_ylabel('PER (배수, 배)', fontproperties=font_label)
    ax.set_title('글로벌 메모리 반도체 밸류에이션(PER) 비교 — 한국 기업의 압도적 저평가', fontproperties=font_title, pad=15, color=NAVY)
    ax.legend(prop=font_label)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for rects in [r1, r2, r3]:
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f"{h:.1f}x",
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontproperties=font_value, fontsize=8)
            
    save_chart(fig, "memory_peers_valuation.png")


# -------------------------------------------------------------
# 4. Samsung Electronics Foundry Price Hike by Node
# -------------------------------------------------------------
def make_foundry_price_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), facecolor='white')
    ax1.set_facecolor(LIGHT_BG)
    ax2.set_facecolor(LIGHT_BG)
    
    # Left: Price hike by node
    nodes = ['4나노 (SF4)\n[미국/중국]', '4나노 (SF4)\n[대만]', '5나노 (SF5)\n[웨이퍼 기준]', '8나노\n[레거시 공정]']
    hikes = [15.0, 10.0, 15.0, 10.0]
    min_hikes = [10.0, 5.0, 10.0, 10.0]
    
    x = np.arange(len(nodes))
    bars = ax1.bar(nodes, hikes, color=[NAVY, NAVY_LIGHT, BLUE, GRAY], width=0.5, alpha=0.9)
    ax1.set_ylabel('인상률 상단 (%)', fontproperties=font_label)
    ax1.set_title('삼성전자 공정별 파운드리 가격 인상률', fontproperties=font_title, pad=12, color=NAVY)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for i, bar in enumerate(bars):
        h = bar.get_height()
        low = min_hikes[i]
        text = f"+{low:.0f}~{h:.0f}%" if low != h else f"+{h:.0f}%"
        ax1.annotate(text,
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
    
    # Right: Revenue Breakdown shift (AI/HPC & Advanced Nodes)
    categories = ['첨단 공정 비중\n(SF5 이하)', 'AI / HPC 매출 비중\n(2025년 말)', 'AI / HPC 매출 비중\n(2026년 목표)']
    shares = [52.0, 17.5, 32.0]
    
    bars2 = ax2.bar(categories, shares, color=[PURPLE, GRAY, GREEN], width=0.5, alpha=0.9)
    ax2.set_ylabel('매출 비중 (%)', fontproperties=font_label)
    ax2.set_title('삼성전자 파운드리 고부가 AI·첨단 비중 확대', fontproperties=font_title, pad=12, color=NAVY)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
        
    plt.tight_layout()
    save_chart(fig, "samsung_foundry_expansion.png")


# -------------------------------------------------------------
# 5. Isu Petasys: Multi-Lam Share & Capacity Roadmap
# -------------------------------------------------------------
def make_isupetasys_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), facecolor='white')
    ax1.set_facecolor(LIGHT_BG)
    ax2.set_facecolor(LIGHT_BG)
    
    # Left: Multi-Lam Share
    quarters = ['1Q26\n(실적)', '2Q26\n(실적)', '현재 수주잔고\n(가시성)']
    shares = [7.0, 11.0, 22.0]
    
    bars1 = ax1.bar(quarters, shares, color=[GRAY, BLUE, GREEN], width=0.45, alpha=0.9)
    ax1.set_ylabel('Multi-Lam 비중 (%)', fontproperties=font_label)
    ax1.set_title('이수페타시스 고부가 Multi-Lam 비중 추이', fontproperties=font_title, pad=12, color=NAVY)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}%" if h < 20 else "20%+",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
    
    # Right: Monthly Capa Roadmap
    periods = ['현재\n(2026.8)', '2027년 2Q\n(증설 1차)', '2028년 하반기\n(증설 2차)']
    capa = [1200, 1500, 1800]
    
    lines = ax2.plot(periods, capa, marker='o', color=NAVY, linewidth=2.5, markersize=8)
    ax2.set_ylabel('월 매출 Capa (억원)', fontproperties=font_label)
    ax2.set_title('이수페타시스 월 생산능력(Capa) 증설 로드맵', fontproperties=font_title, pad=12, color=NAVY)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_ylim(1000, 2000)
    
    for i, txt in enumerate(capa):
        ax2.annotate(f"{txt:,}억원/월\n(+{((txt-1200)/1200)*100:.0f}%)" if txt > 1200 else f"{txt:,}억원/월",
                     xy=(periods[i], txt),
                     xytext=(0, 10), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
        
    plt.tight_layout()
    save_chart(fig, "isupetasys_growth.png")


# -------------------------------------------------------------
# 6. Sector Rotation: Bio/Pharma Stock Surge (Moderna, etc.)
# -------------------------------------------------------------
def make_bio_rotation_chart():
    fig, ax = plt.subplots(figsize=(10, 4.8), facecolor='white')
    ax.set_facecolor(LIGHT_BG)
    
    stocks = ['모더나\n(Moderna)', '바이오엔텍\n(BNTX)', 'LABU\n(바이오3X)', '머크\n(MSD)', '일라이릴리\n(LLY)', '암젠\n(AMGN)', '화이자\n(PFE)', 'NBI\n(나스닥바이오)']
    returns = [77.0, 22.0, 13.45, 11.17, 4.5, 4.0, 3.6, 4.86]
    
    colors = [RED if r > 50 else (GOLD if r > 10 else BLUE) for r in returns]
    
    bars = ax.bar(stocks, returns, color=colors, width=0.55, alpha=0.9)
    ax.set_ylabel('일일 주가 등락률 (%)', fontproperties=font_label)
    ax.set_title('8월 19일 미국 헬스케어·바이오 섹터 급등률 (키트루다+mRNA 암백신 3상 호재)', fontproperties=font_title, pad=15, color=NAVY)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"+{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value, fontsize=8.5)
        
    save_chart(fig, "bio_sector_surge.png")


# -------------------------------------------------------------
# 7. Unitree IPO & Humanoid Cost Comparison
# -------------------------------------------------------------
def make_humanoid_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), facecolor='white')
    ax1.set_facecolor(LIGHT_BG)
    ax2.set_facecolor(LIGHT_BG)
    
    # Left: BOM Cost Comparison (China vs US)
    countries = ['중국 Unitree 등\n(모건스탠리 추정)', '미국 제조사\n(모건스탠리 추정)']
    costs = [4.6, 13.1]
    
    bars1 = ax1.bar(countries, costs, color=[GREEN, RED], width=0.45, alpha=0.9)
    ax1.set_ylabel('대당 소재비 (만 달러, $10k)', fontproperties=font_label)
    ax1.set_title('휴머노이드 로봇 대당 소재비(BOM) 비교', fontproperties=font_title, pad=12, color=NAVY)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"${h:.1f}만\n({h/13.1*100:.0f}%)",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
        
    # Right: Unitree Market Cap vs 2026 Sales & Valuation Multiple
    metrics = ['2026E 매출\n(22억 위안)', '상장 당일 종가 시총\n(3,418억 위안)', 'PSR 60배\n(초고성장 기준가)', '실제 상장 PSR\n(155배)']
    vals = [2.2, 341.8, 132.0, 341.8] # in 10B RMB or multiples
    
    labels_val = ['22억 위안', '3,418억 위안', '1,320억 위안', 'PSR 155배']
    
    bars2 = ax2.bar(['2026 매출', '종가 시총', 'PSR 60배 기준가'], [2.2, 341.8, 132.0], color=[GRAY, RED, GOLD], width=0.45, alpha=0.9)
    ax2.set_ylabel('규모 (십억 위안, 10억 RMB)', fontproperties=font_label)
    ax2.set_title('유니트리(Unitree) 시가총액과 밸류에이션 과열도', fontproperties=font_title, pad=12, color=NAVY)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}억 RMB",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha='center', va='bottom', fontproperties=font_value)
        
    plt.tight_layout()
    save_chart(fig, "humanoid_unitree_analysis.png")


if __name__ == "__main__":
    make_macro_chart()
    make_skhynix_return_chart()
    make_memory_valuation_chart()
    make_foundry_price_chart()
    make_isupetasys_chart()
    make_bio_rotation_chart()
    make_humanoid_chart()
    print("All charts generated successfully!")
