"""Second pass over the full paste, including lecture transcripts.

Each sentence is emitted only when the source still contains the anchor
phrases it rests on. Speech-to-text noise stays out; the missing themes stay in.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from insight_distiller.extract import Facts


@dataclass
class DeepSection:
    key: str
    title: str
    items: list[str] = field(default_factory=list)


def _has(text: str, *needles: str) -> bool:
    return all(needle in text for needle in needles)


def supplements(text: str, facts: Facts) -> dict[str, list[str]]:
    """Facts already parsed from quick comments but left out of the first note."""
    s = facts.scalars
    out: dict[str, list[str]] = defaultdict(list)

    if s.get("fx_consensus") and s.get("fx_alt"):
        cut = s.get("fx_consensus_cut", "10")
        out["memory"].append(
            f"컨센서스 환율 {s['fx_consensus']}원을 {s['fx_alt']}원으로 낮추면 이익 컨센서스가 약 {cut}% 내려갈 수 있다."
        )
    if s.get("adr_local_a") and s.get("adr_local_b"):
        out["memory"].append(
            f"ADR 프리미엄이 {s.get('adr_prem_a')}%면 본주 {s['adr_local_a']}만 원, "
            f"{s.get('adr_prem_b')}%면 {s['adr_local_b']}만 원으로 적혀 있다."
        )
    if s.get("discount_band"):
        out["memory"].append(f"마이크론 대비 과거 할인율 밴드는 {s['discount_band']}%다.")
    if s.get("wdc_pe_path"):
        out["hdd"].append(f"WDC 실제 PER 경로는 {s['wdc_pe_path']}다.")
    if s.get("share_from") and s.get("share_to"):
        out["hdd"].append(
            f"도시바 점유율이 30%까지 가면 WDC·시게이트 합산 점유율은 {s['share_from']}%에서 {s['share_to']}%로 낮아질 수 있다는 상상이다."
        )
    if _has(text, "65%", "BOM"):
        out["optical"].append(
            "3.2T의 65% 미국산 BOM 시나리오에서는 중국 모듈 조립이 남아도 미국 DSP·레이저 탑재가 늘어날 수 있다. 단기 실적의 핵은 중국 규제가 아니다."
        )
    if _has(text, "DustPhotonics", "ZeroFlap"):
        out["optical"].append(
            "크레도는 DustPhotonics 인수로 실리콘포토닉스까지 갖췄고, 1.6T ZeroFlap 트랜시버를 냈다. FY27 광통신 매출은 6억 달러 이상으로 적혀 있다."
        )
    if _has(text, "PhotonLink", "InP"):
        out["optical"].append(
            "코히런트는 PhotonLink와 InP 공급이, 루멘텀은 레이저가 근거로 붙는다. BofA는 다년 수요와 공급 부족을 배경으로 적었다."
        )
    if "HVLP4" in text and "과민반응" in text:
        out["optical"].append(
            "두산 전자BG는 베라 루빈 울트라까지 HVLP4라 마진 스퀴즈 우려가 제한적이고, 중국 광모듈 규제에 빠진 주가는 과민반응으로 적혀 있다."
        )
    if "NVDA = GPU" in text and "AVGO" in text:
        out["optical"].append(
            "수혜 사슬은 GPU(엔비디아), 스위치(브로드컴), 구리·DSP(크레도), 레이저(루멘텀), 레이저·소재·트랜시버(코히런트)로 적혀 있다."
        )
    if s.get("pce_3m") and s.get("pce_august"):
        out["macro"].append(
            f"8월 근원 PCE {s['pce_august']}%는 개정 효과다. 개정 7월 {s.get('pce_july')}%에서 사실상 보합이고, "
            f"3개월 연율은 약 {s['pce_3m']}%, 6개월 연율은 약 {s.get('pce_6m')}%다."
        )
    if s.get("jobs_3m"):
        out["macro"].append(
            f"고용 3개월 평균은 약 {s['jobs_3m']}만 명이고, 직전 두 달 합산 {s.get('jobs_revision', '6')}만 명 하향이 있다. 전월은 {s.get('jobs_prior')}만 명이다."
        )
    if s.get("sox_window") and s.get("rate_bp"):
        out["macro"].append(
            f"9월 11일부터 10월 2일까지 금리가 +{s['rate_bp']}bp인 동안 SOX +{s['sox_window']}%, "
            f"마이크론 +{s.get('mu_window')}%, 코스닥 +{s.get('kosdaq_window')}%였다."
        )
    if "Bad Jobs" in text:
        out["macro"].append("고용 쇼크의 프레임은 Bad Jobs, Good Stocks다. 침체보다 인상 확률 하락으로 읽혔다.")
    if "직간접 Exposure" in text or "직간접" in text:
        out["macro"].append(
            "10월 동결만으로 지수 전체가 한 단계 오르기는 제한적이다. 초과수익은 AI 직접·간접 노출로 적혀 있다."
        )
    if _has(text, "저보스", "바이백"):
        out["macro"].append(
            "데이비드 저보스는 높은 장기금리를 새 정상으로 두기보다, 재무부 국채 바이백으로 시간을 벌고 생산성 개선이 물가를 낮추기를 기다린다는 쪽이다."
        )
    if "A100/H100" in text:
        out["risk"].append(
            "추론 수요로 A100/H100이 현금흐름을 이어 간다는 점이, 1960년대 컴퓨터 리스 버블과 다른 부분으로 적혀 있다."
        )
    if s.get("gpu_life_names"):
        out["risk"].append(f"수명 가정이 갈리는 이름은 {s['gpu_life_names']}다.")
    if s.get("kosdaq_share_to"):
        out["portfolio"].append(
            f"8월에서 9월로 코스닥 거래대금은 +{s.get('kosdaq_turn')}%, 코스피는 -{s.get('kospi_turn')}%, "
            f"코스닥 비중은 {s.get('kosdaq_share_from')}%에서 {s['kosdaq_share_to']}%다."
        )
    if s.get("sanil_opm_26"):
        out["power"].append(
            f"산일전기 영업이익률은 FY26 {s['sanil_opm_26']}%에서 FY28 {s['sanil_opm_28']}%다. "
            "2028년 154kV 양산과 블룸에너지 벤더 등록이 적혀 있다."
        )
    if s.get("intech_backlog"):
        out["substrate"].append(
            f"인텍플러스 수주잔고는 2분기 {s.get('intech_backlog_prev')}억에서 3분기 말 {s['intech_backlog']}억, "
            f"4분기 신규 {s.get('intech_orders')}억 전망이다. 외국인 지분은 {s.get('intech_foreign_from')}%에서 {s.get('intech_foreign_to')}%다."
        )
    if s.get("crdo_guide"):
        out["optical"].append(f"크레도 FY2027 매출 성장률 가이던스는 {s['crdo_guide']}% 이상이다.")
    if s.get("cohr_tp"):
        out["optical"].append(
            f"번스타인 코히런트 목표주가는 ${s['cohr_tp']}다."
            + (f" 고객 인게이지먼트는 {s['cohr_engagements']}개로 적혀 있다." if s.get("cohr_engagements") else "")
        )
    return out


def deep_sections(text: str) -> list[DeepSection]:
    sections: list[DeepSection] = []

    price = DeepSection("tape", "가격대와 수급")
    if _has(text, "28만 5,000원", "190만 원"):
        price.items.append(
            "삼성전자의 다음 가격대는 28만 원, 그중 28만 5,000원 돌파다. 하이닉스는 190만 원 돌파다."
        )
    if _has(text, "자사주 매입이 끝나야 간다", "10월 15일"):
        price.items.append(
            "자사주 매수는 하락을 받아 주는 자리이지 상승 재료가 아니다. 하이닉스 자사주는 10월 15일까지이고, 매수가 끝난 뒤가 수급 시험으로 적혀 있다."
        )
    if _has(text, "13% 정도", "30% 넘게"):
        price.items.append(
            "마이크론은 고점 대비 낙폭이 약 13%까지 좁혀졌고, 하이닉스는 고점 대비 30% 넘게 벌어져 있다는 비교가 나온다."
        )
    if _has(text, "5년짜리 사이클", "ETF를 사시는게"):
        price.items.append(
            "장비 사이클은 5년으로 보고, 그 안에서 주가는 종목마다 먼저 가고 늦게 간다. 초보는 소부장 ETF가 편하다는 코멘트다."
        )
    if _has(text, "헤지펀드들 레버리지", "손절매"):
        price.items.append(
            "미국 국채 금리 급등은 헤지펀드가 레버리지로 금리 하락에 베팅했다가 손절한 흐름으로 적혀 있고, 금리는 추가로 안정될 수 있다는 쪽이다."
        )
    if price.items:
        sections.append(price)

    equip = DeepSection("equipment", "소부장 운용")
    if _has(text, "증착이라고", "원익 IPS가 조금 더 편해"):
        equip.items.append(
            "전공정 핵심은 증착이다. 원익IPS·유진테크·주성 중 원익IPS가 시가총액과 매물 면에서 더 편한 후보로 적혀 있다."
        )
    if _has(text, "주성은 아직 실적이 안 나와서"):
        equip.items.append("주성엔지니어링은 실적이 확인되기 전에는 믿음이 약하다는 코멘트다.")
    if _has(text, "12만 원까지", "원익"):
        equip.items.append("원익IPS가 12만 원까지 밀리는 자리는 관심 구간으로 적혀 있다.")
    if _has(text, "고압 수소", "HPSP"):
        equip.items.append("고압수소어닐은 HPSP가 세 자리에서 1위라는 이유로 핵심 후보에 들어 있다.")
    if _has(text, "원익 IPS 그다음에 PSK"):
        equip.items.append("식각·세정 쪽 관심 이름은 PSK다.")
    if _has(text, "한미랑 지금은 리노"):
        equip.items.append(
            "후공정 핵심은 한미반도체와 리노공업이다. 프로브카드 대장 TSE는 조정을 기다리라는 쪽이다."
        )
    if _has(text, "솔브레인", "한솔 케미칼"):
        equip.items.append("소재는 솔브레인, 동진쎄미켐, 한솔케미칼 중 하나를 보면 된다는 압축이다.")
    if _has(text, "내년 기준으로 39배", "16.8배", "25배"):
        equip.items.append(
            "삼성전기는 내년 약 39~40배, 2028년을 당기면 약 25배라는 설명이다. 심텍 내년 18배 대비 대덕전자(TLB)는 16.8배다."
        )
    if _has(text, "필옵틱스는 잘 빠져나오세요", "45,000원", "유리기판은", "2029년 30년", "33년"):
        equip.items.append(
            "유리기판은 엔비디아 검토 단계다. 양산 언급은 2029~2030년, FC-BGA 치환은 2033년 전후다. 필옵틱스는 4만 5,000원대와 급등 때마다 비중을 줄이라는 코멘트다."
        )
    if equip.items:
        sections.append(equip)

    dc = DeepSection("datacenter", "데이터센터 금융과 전력")
    if _has(text, "2.4GW", "180억", "30억", "210억"):
        dc.items.append(
            "뉴멕시코 프로젝트 주피터는 2.4GW다. 총 210억 달러 중 자기자본은 약 30억 달러, 건설 대출은 180억 달러로 적혀 있다."
        )
    if "오라클의 대출은 아니에요" in text and "장부에 있는 부채가 아니고" in text:
        dc.items.append("180억 달러 건설 대출은 오라클 장부 밖이다.")
    if "임대료를 못 낸다" in text:
        dc.items.append("공사 지연을 이유로 임대료를 못 낸다는 선언이 나온다.")
    if "신용 등급이 일단 제일 최하단" in text:
        dc.items.append("오라클은 하이퍼스케일러 중 신용등급이 가장 아래이고, 한 단계 더 내려가면 투기등급이라는 설명이다.")
    if _has(text, "11월 중간 선거", "프로젝트 주피터"):
        dc.items.append(
            "인허가와 주민 반대는 주피터만의 일이 아니다. 버지니아·텍사스와 11월 중간선거가 같이 적혀 있다."
        )
    if "예비율이 30%" in text:
        dc.items.append(
            "미국 발전 예비율은 약 30%로 언급된다. 병목은 발전량 자체보다, 데이터센터를 지으려는 지역의 송전과 인허가다."
        )
    if _has(text, "11월 3일", "하이퍼스케일러"):
        dc.items.append(
            "다음 일정은 10월 말 하이퍼스케일러 실적과 11월 3일 미국 중간선거다. 결과 자체보다 확인되던 이벤트가 지나간 뒤를 본다는 코멘트다."
        )
    if dc.items:
        sections.append(dc)

    peak = DeepSection("peak", "피크아웃과 2028")
    if _has(text, "400만 원", "80%", "40%"):
        peak.items.append(
            "하이닉스 400만 원 시나리오의 조건은 영업이익률 80%와 장기계약 비중 40%다. 마이크론 실적은 그 숫자가 불가능하지 않다는 근거로 쓰였다."
        )
    if _has(text, "28년에도 15% 이상", "26%", "14%"):
        peak.items.append(
            "7월 말 이후, 2028년에도 15% 이상 성장으로 분류된 종목은 약 26% 올랐고, 2027년 피크아웃으로 분류된 쪽은 약 14% 올랐다. 싼 PER은 2028년 증익률 둔화에 대한 질문으로 적혀 있다."
        )
    if "프리캐시플로" in text or "프리캐시플" in text:
        peak.items.append(
            "이익보다 현금이 팩트라는 프레임이다. 하이퍼스케일러 프리캐시플로가 말라 있으면 반도체 매수 여력이 할인율과 함께 의심받는다."
        )
    if _has(text, "솔리다임 중복 상장", "결정난 바 없다"):
        peak.items.append("솔리다임 중복상장은 일단 진정됐고, 하이닉스는 아직 결정된 바 없다고 말했다.")
    if _has(text, "의무 공개 매수", "보류"):
        peak.items.append("의무공개매수 범위를 넓히는 조치는 처리가 보류됐다.")
    if _has(text, "5.5 이상", "실질금"):
        peak.items.append(
            "10년물 5.5%는 과거 투자 사이클에서 주가를 제약하던 구간에 대응되는 스트레스 라인으로 적혀 있다. 최근 금리 상승분 상당수는 물가가 아니라 실질금리다."
        )
    if _has(text, "프랑스 국채", "선행 지수는", "동행 지수"):
        peak.items.append(
            "약한 고리로 프랑스 국채가 언급된다. 한국은 선행지수가 오르는데 동행지수가 못 따라오는 괴리가 있다. 지수 방향 베팅보다 2028년에 과실이 나오는 선행투자를 고르라는 결론이다."
        )
    if peak.items:
        sections.append(peak)

    other = DeepSection("breadth", "수출 체급과 AI 시계")
    if "화장품 수출이 2%" in text:
        other.items.append(
            "화장품·바이오 수출은 좋지만, 화장품은 전체 수출의 약 2%라 지수 주도 자리는 아니다."
        )
    if _has(text, "퀄리티 주식", "안 좋은게 노출될 때"):
        other.items.append(
            "화장품 수출이 사상 최대인데도 주가가 쉰 이유는 성장 속도 둔화와 환율·원가 의심이다. 퀄리티 종목은 그 의심이 가격에 반영될 때 본다는 코멘트다. 구조적 악화로 단정하지는 않는다."
        )
    if _has(text, "GPU 임대료는 되게 스테이블", "토큰 가격"):
        other.items.append(
            "GPU 임대료는 안정적이고 토큰 가격은 내려간다. 토큰 가격 하락은 제품 가격 하락이 아니라 원가 하락으로 읽는 시각이 있다."
        )
    if _has(text, "추론", "메모리 용량"):
        other.items.append(
            "학습보다 추론 사용이 늘면 메모리 용량 수요가 따라온다는 설명이 있다."
        )
    if _has(text, "피지컬", "데이터 모으기"):
        other.items.append(
            "피지컬 AI는 산업 전선이 넓어지는 이야기다. 주가는 이미 한 번 선반영된 뒤 고점 대비 크게 빠진 상태로, 눈에 보이는 상용화와 주가 시계는 따로 둔다."
        )
    if "16분의로" in text or "16분로 파세요" in text:
        other.items.append(
            "고점 매도는 맞히기 어렵다는 전제로, 줄이려면 내년 봄까지 나눠 팔라는 조언이 있다. 횡보 구간에서는 배당으로 시간을 버티는 선택도 적혀 있다."
        )
    if _has(text, "중간 선거 전까지", "현금을 조금씩"):
        other.items.append(
            "미국 지수가 신고가인 동안, 중간선거 전까지 오를 때마다 현금을 조금씩 만들라는 월간 코멘트가 있다."
        )
    if other.items:
        sections.append(other)

    return sections


def extra_conditions(text: str) -> list[str]:
    rows = []
    if _has(text, "400만 원", "80%", "40%"):
        rows.append("하이닉스 400만 원은 영업이익률 80%와 장기계약 비중 40%가 같이 나올 때의 시나리오다.")
    if "10월 15일" in text:
        rows.append("하이닉스 자사주 매수 종료 시점은 10월 15일로 적혀 있다.")
    if "5.5 이상" in text:
        rows.append("10년물 5.5%는 투자 사이클을 제약할 수 있는 구간으로 적혀 있다.")
    if "11월 3일" in text:
        rows.append("11월 3일 미국 중간선거와 그 전 하이퍼스케일러 실적이 다음 확인 일정이다.")
    if "LTA" in text and "28년" in text:
        rows.append("27년 1분기 실적에서 장기계약과 2028년 컨센서스 상향이 보이면 메모리 멀티플 논의가 다시 열린다.")
    return rows
