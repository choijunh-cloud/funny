#!/usr/bin/env python3
"""추가 증류가 10월 9일 원문 밖 숫자를 만들지 않는지 확인한다."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from distill_followup import DEFAULT_FOLLOW, build_followup_report, main  # noqa: E402
from distill_insights import assert_grounded, clean_transcript, normalize  # noqa: E402


class FollowupDistillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = DEFAULT_FOLLOW.read_text(encoding="utf-8")
        cls.report = build_followup_report(cls.raw, DEFAULT_FOLLOW.name)
        cls.flat = normalize("\n".join(clean_transcript(cls.raw)))

    def test_new_facts_are_in_the_source(self):
        values = {fact.value for fact in self.report.facts}
        for token in ("15~20%", "약 38%", "4.5~6.0%", "3.4~5.1%", "+226.2%", "2029년 초", "190조원"):
            self.assertIn(token, values)
        self.assertEqual(self.report.missing, [])

    def test_cards_stay_grounded(self):
        assert_grounded(self.report.headline, self.flat, "headline")
        self.assertGreaterEqual(len(self.report.insights), 8)
        for insight in self.report.insights:
            assert_grounded(insight.verdict + insight.action + insight.avoid, self.flat, insight.title)
            self.assertTrue(insight.evidence)

    def test_writes_addendum_and_keeps_oct8(self):
        main()
        text = (ROOT / "lectures" / "10월 9-11일 추가 인사이트.md").read_text(encoding="utf-8")
        self.assertIn("15~20%", text)
        combined = (ROOT / "lectures" / "10월 8-11일 투자 인사이트.md").read_text(encoding="utf-8")
        self.assertIn("107조 4천억", combined)
        self.assertIn("15~20%", combined)
        self.assertGreater((ROOT / "lectures" / "10월 9-11일 추가 인사이트.docx").stat().st_size, 8_000)


if __name__ == "__main__":
    unittest.main()
