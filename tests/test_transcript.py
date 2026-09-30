"""오늘 방송 전사에서 결론 문장이 안내 멘트보다 앞에 오는지."""

from insights.transcript import distill_transcript, distill_transcript_path
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "data" / "raw" / "clean_script_3.txt"

FIXTURE = """
카카오톡 채널 머니랩 추가하시기 바라고요. 모든 투자 판단의 책임은 투자자분들께 있습니다.
금리가 올라가도 AI 성장이 금리보다 더 나오니까 시장은 아직은 견조하다 이렇게 봐야 됩니다.
혁명기에는 금리가 오르지만 주가도 같이 오른다. 자금 조달 수요 때문이라는 것이 핵심입니다.
메모리를 아직 사이클 산업, 천민처럼 본다. 없는데 못 파는 건 수급 문제다.
HBM에서 마이크론이 흔들리면 삼성전자와 하이닉스 몫이 늘어나는 반대 급부다.
전통적인 시각은 PBR이고 장기 계약 B2B가 늘면 PER로 볼 수 있다는 논쟁이다.
박스에서 오를 때 사고 내릴 때 손절하면 계좌가 깨진다. 주도주를 들고 버티는 편이 낫다.
"""


def test_fixture_keeps_the_argument_and_drops_the_promo():
    study = distill_transcript(FIXTURE)
    blob = " ".join(piece.point for piece in study.pieces)
    assert "카카오톡" not in blob
    assert "책임" not in blob
    assert any("금리" in piece.point or "혁명" in piece.point for piece in study.pieces)
    assert any("주도" in piece.point or "손절" in piece.point for piece in study.pieces)


def test_today_script_distills_the_learning_logic():
    study = distill_transcript_path(SCRIPT)
    by = {piece.theme: piece for piece in study.pieces}
    labels = " ".join(piece.label for piece in study.pieces)
    points = " ".join(piece.point + " " + " ".join(piece.support) for piece in study.pieces)
    assert "금리" in labels
    assert "HBM" in labels or "메모리" in labels
    assert "주도" in labels or "박스" in labels
    assert any(word in points for word in ("성장", "혁명", "금리"))
    assert any(word in points for word in ("HBM", "마이크론", "마이크로", "사이클"))
    assert "카카오톡" not in points
    assert "시각화" not in points
    assert study.stats["pieces"] >= 6
    rates = by["rates"].point + " " + " ".join(by["rates"].support)
    assert "성장" in rates
    assert "혁명" in rates
    assert "유가" in by["oil"].point
    memory = by["memory"].point + " " + " ".join(by["memory"].support)
    assert "천민" in memory or "사이클" in memory
    assert "못 팔" in memory or "수급" in memory
    action = by["action"].point + " " + " ".join(by["action"].support)
    assert "손절" in action
    assert any(word in action for word in ("수면제", "버티", "주도"))
    hbm = by["hbm"].point + " " + " ".join(by["hbm"].support)
    assert "HBM" in hbm
    assert any(word in hbm for word in ("나눠", "반대", "수율"))
    assert study.chain
    assert any("채권" in title or "밸류" in title for title, _left, _right in study.forks)
    assert any("손절" in quote for _label, quote in study.actions)
