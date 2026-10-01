"""추출기와 전체 증류 파이프라인 검증."""

from __future__ import annotations

import unittest
from pathlib import Path

from insight_distiller.extract import extract
from insight_distiller.models import Chunk
from insight_distiller.pipeline import run
from insight_distiller.textutil import money_b_from_eok, repair_ocr

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"


def chunk(text: str, kind: str = "txt", source: str = "fixture") -> Chunk:
    return Chunk(source, kind, "fixture", text, 0.9)


class MoneyTests(unittest.TestCase):
    def test_eok_dollar_converts_to_billions(self):
        self.assertEqual(money_b_from_eok("542.3"), "$54.23B")
        self.assertEqual(money_b_from_eok("1,331.9"), "$133.19B")
        self.assertEqual(money_b_from_eok("615"), "$61.5B")

    def test_ocr_repairs_known_table_breaks(self):
        repaired = repair_ocr("2026년 3596 — 웨이퍼\n비중 709\n704만주(1990)")
        self.assertIn("2026년 35%", repaired)
        self.assertIn("비중 70%", repaired)
        self.assertIn("704만주(19%)", repaired)


class MicronExtractTests(unittest.TestCase):
    def test_ir_block_and_guidance(self):
        text = """
        마이크론 FQ4 2026 실적 IR
        [FQ4 실적]
        매출 542.3억 달러 (QoQ +31%, YoY +379%)
        매출총이익률 87.0% (+210bp)
        영업이익 446.4억 달러 (이익률 82.3%)
        EPS 33.42달러 (QoQ +33%)
        조정 FCF 332.0억 달러
        [FY26 연간]
        매출 1,331.9억 달러 (+256%)
        EPS 75.52달러 (+811%)
        [가이던스]
        FQ1 매출 615억 ± 15억 달러, 매출총이익률 약 86.25%
        EPS 38.15 ± 1.00달러
        FQ1이 매출총이익률 저점(인센티브 비용의 재고 반영), 이후 상승
        [SCA·RPO]
        SCA 26건 체결, 2030년까지 매출의 35% 이상 추정
        예상 매출의 3/4은 가격 체계 확정
        고객 재무 약정 320억 달러, RPO 약 1,500억 달러
        """
        facts = {fact.key: fact.display for fact in extract([chunk(text)])}
        self.assertEqual(facts["mu_q4_revenue"], "$54.23B")
        self.assertEqual(facts["mu_q4_yoy"], "+379%")
        self.assertEqual(facts["mu_q4_op"], "$44.64B")
        self.assertEqual(facts["mu_q4_eps"], "$33.42")
        self.assertEqual(facts["mu_fy_revenue"], "$133.19B")
        self.assertEqual(facts["mu_q1_rev_mid"], "$61.5B")
        self.assertEqual(facts["mu_q1_gpm"], "86.25%")
        self.assertEqual(facts["sca_2030_share"], "35% 이상")
        self.assertEqual(facts["sca_rpo"], "$150B")
        self.assertIn("mu_gpm_trough", facts)

    def test_korean_guidance_consensus(self):
        text = """
        • 조정 EPS: $37.15~39.15 → 시장 예상 $35.47 상회
        • 매출: $60~63B → 시장 예상 $57.4B 상회
        • 중간값 기준 매출 $61.5B, 전분기 대비 약 +13.4%
        """
        facts = {fact.key: fact.display for fact in extract([chunk(text, "pdf_text")])}
        self.assertEqual(facts["mu_q1_rev_cons"], "$57.4B")
        self.assertEqual(facts["mu_q1_eps_cons"], "$35.47")
        self.assertEqual(facts["mu_q1_rev_qoq"], "+13.4%")


class SamsungExtractTests(unittest.TestCase):
    def test_range_bullets(self):
        text = """
        4Q DRAM ASP +3~11%, NAND +6~11%로 차이가 커서
        • 27년 OP: 346~609조원 → 전망 격차 263조원
        • 28년 OP: 254~715조원 → 격차 461조원
        • TP: 27~56만원 (유안타 63만원을 포함하면 27~63만원)
        • Target PBR: 1.9~3.7배
        • ROE: 35~56% (NH 제외)
        """
        facts = {fact.key: fact.display for fact in extract([chunk(text, "pdf_text")])}
        self.assertEqual(facts["sec_op_2027"], "346~609조원")
        self.assertEqual(facts["sec_op_2027_gap"], "263조원")
        self.assertEqual(facts["sec_op_2028_gap"], "461조원")
        self.assertEqual(facts["sec_tp_yuanta"], "63만원")
        self.assertEqual(facts["sec_dram_asp_4q"], "+3~11%")
        self.assertEqual(facts["sec_nand_asp_4q"], "+6~11%")

    def test_broker_rows_and_aliases(self):
        text = """
        릉국증권 9/29 103.4 114.9 560,000
        05투자증권 9/29 103.0 118.5 530,000
        TESA 9/23 100.0 111.9 630,000
        키움증권 9/22 107.0 111.0 350,000
        """
        rows = [fact.display for fact in extract([chunk(text, "pdf_ocr")]) if fact.key == "sec_broker_op"]
        self.assertEqual(len(rows), 4)
        self.assertIn("흥국", rows[0])
        self.assertIn("DS", rows[1])
        self.assertIn("유안타", rows[2])
        self.assertIn("63만원", rows[2])


class PipelineTests(unittest.TestCase):
    def test_full_distillation_reads_every_source(self):
        if not SOURCES.exists():
            self.skipTest("sources 디렉터리가 없습니다")
        out = ROOT / "output"
        knowledge = run(SOURCES, out, ocr=True)
        names = {row["source"] for row in knowledge.documents}
        self.assertEqual(len(names), 5)
        pptx = next(row for row in knowledge.documents if row["source"].endswith(".pptx"))
        self.assertGreaterEqual(pptx["chunks"], 14)
        note = next(row for row in knowledge.documents if row["source"].endswith(".txt"))
        self.assertGreater(note["chars"], 100_000)
        keys = {fact.key for fact in knowledge.facts}
        for required in (
            "mu_q4_revenue",
            "mu_q1_rev_mid",
            "mu_q4_gpm",
            "sec_op_2027",
            "sec_dram_asp_4q",
            "sfa_cancel",
            "hbm4e_not_inhouse",
            "supply_tight",
        ):
            self.assertIn(required, keys, required)
        self.assertTrue(knowledge.equipment["summary"])
        self.assertGreaterEqual(len(knowledge.equipment["sections"]), 8)
        report = (out / "투자인사이트.md").read_text(encoding="utf-8")
        for needle in (
            "54.23",
            "61.5",
            "$38.15",
            "346~609",
            "19%",
            "70%",
            "원익IPS",
            "HPSP",
            "한미반도체",
            "SCA",
            "파운드리",
            "27%",
            "595.8",
            "DS (",
        ):
            self.assertIn(needle, report, needle)
        self.assertNotIn("EPS 중간값 $27", report)
        self.assertNotRegex(report, r"\$33\.(?!\d)")
        self.assertIn("2026년 35%", report)
        self.assertTrue((out / "knowledge.json").exists())


if __name__ == "__main__":
    unittest.main()
