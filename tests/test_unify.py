"""두 해석 편과 퀵 코멘트가 한 편의 판단으로 겹치는지."""

from pathlib import Path

from insights.html_essay import parse_essay
from insights.unify import unify

ROOT = Path(__file__).resolve().parents[1]
QUICK = ROOT / "data" / "raw" / "2026-09-29_quick_comments.txt"
HTML = ROOT / "data" / "raw" / "html"

FIXTURE = """
<!doctype html><html lang="ko"><body><div class="wrap"><div class="hdr">
<div class="eyebrow">해석 편</div>
<h1>서두르지 않는 브레이크</h1>
<p class="sub">금리를 보되 금리에 지지 말라</p>
</div>
<section id="s01"><h2><span class="snum">01</span>금리</h2>
<p class="lede">금리는 밸류에이션의 천장이지 실적의 바닥이 아니다.</p>
<div class="say"><b>말하는 바</b> — 지금의 금리 상승은 투자 증대의 결과물이다.</div>
<div class="mean"><b>의미</b> — 금리를 두려워하지 말고 실적이 천장을 미는지 보라. <span class="tag inf">해석</span></div>
<div class="look"><b>보라는 것</b> — 오늘 밤 PCE와 마이크론.</div>
<svg><text>이 그림 숫자는 본문이 아니다 999조</text></svg>
</section>
<section id="sx"><h2><span class="snum">X</span>부록</h2>
<div class="say"><b>말하는 바</b> — 이 실측은 본문에 오면 안 된다.</div>
</section>
<div class="moral"><b>비유.</b> 브레이크를 보되, 브레이크에 지지 마라.</div>
<div class="spk"><div class="card"><h3><span>김효진</span><span class="sub">모닝</span></h3>
<p>금리는 절벽이 아니라 부식제다.</p>
<div class="cap">처방 · 금리보다 빨리 크는 기업</div>
</div></div>
</div></body></html>
"""


def test_parser_keeps_speaker_meaning_and_drops_appendix_and_svg():
    essay = parse_essay(FIXTURE)
    assert essay.title == "서두르지 않는 브레이크"
    blob = " ".join(block.text for block in essay.blocks)
    assert "결과물" in blob
    assert "999조" not in blob
    assert "실측은 본문에" not in blob
    assert essay.morals and "지지 마라" in essay.morals[0]
    assert essay.voices[0].name.startswith("김효진")
    assert "부식제" in essay.voices[0].line
    assert "빨리 크는" in essay.voices[0].prescription


def test_unify_folds_both_essays_into_one_brief(tmp_path):
    brake = HTML / "brake.html"
    corrosion = HTML / "corrosion.html"
    if not brake.exists() or not corrosion.exists():
        brake = tmp_path / "brake.html"
        corrosion = tmp_path / "corrosion.html"
        brake.write_text(FIXTURE, encoding="utf-8")
        corrosion.write_text(
            FIXTURE.replace("서두르지 않는 브레이크", "부식제의 시간").replace(
                "결과물이다.", "부식제처럼 오래 머물며 녹인다."
            ),
            encoding="utf-8",
        )
    doc = unify(QUICK, [brake, corrosion])
    labels = [piece.label for piece in doc.pieces]
    assert "금리" in " ".join(labels)
    assert any("결과" in piece.says[0] or "부식" in " ".join(piece.says + piece.readings) for piece in doc.pieces if piece.theme == "rates")
    joined = " ".join(piece.says[0] for piece in doc.pieces if piece.says)
    assert "실측은 본문에" not in joined
    assert doc.stats["pieces"] >= 5
    assert any("괴리" in line or "마이크론" in line for piece in doc.pieces for line in piece.quick)
