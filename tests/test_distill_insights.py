#!/usr/bin/env python3
"""투자 인사이트 증류가 대본 밖의 숫자를 만들지 않는지 확인한다."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from distill_insights import (  # noqa: E402
    DEFAULT_SOURCE,
    assert_grounded,
    build_report,
    clean_transcript,
    normalize,
    write_report,
)


class DistillInsightsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = DEFAULT_SOURCE.read_text(encoding="utf-8")
        cls.report = build_report(cls.raw, DEFAULT_SOURCE.name)
        cls.flat = normalize("\n".join(clean_transcript(cls.raw)))

    def test_timestamps_are_removed(self):
        lines = clean_transcript("본문\n0:07\n7초\n1분 10초\n다음 문장\n")
        self.assertEqual(lines, ["본문", "다음 문장"])

    def test_core_market_facts_exist(self):
        values = {fact.value for fact in self.report.facts}
        for token in ("2조원 정도 팔았습니다", "6조 넘게 팔았습니다", "6625", "5.3", "107조 4천억", "500억 달러"):
            self.assertIn(token, values)

    def test_every_fact_is_a_source_substring(self):
        for fact in self.report.facts:
            self.assertIn(fact.value, self.flat)

    def test_cards_do_not_invent_numbers(self):
        assert_grounded(self.report.headline, self.flat, "headline")
        self.assertGreaterEqual(len(self.report.insights), 10)
        for insight in self.report.insights:
            assert_grounded(insight.verdict + insight.action + insight.avoid, self.flat, insight.title)
            self.assertTrue(insight.evidence)
            for quote in insight.evidence:
                self.assertIn(normalize(quote), self.flat)

    def test_outputs_open(self):
        out = ROOT / "lectures"
        write_report(
            self.report,
            out / "10월 8일 투자 인사이트.md",
            out / "10월 8일 투자 인사이트.docx",
            out / "10월 8일 투자 인사이트.json",
        )
        text = (out / "10월 8일 투자 인사이트.md").read_text(encoding="utf-8")
        self.assertIn("107조 4천억", text)
        self.assertIn("조건과 행동", text)
        self.assertGreater((out / "10월 8일 투자 인사이트.docx").stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
