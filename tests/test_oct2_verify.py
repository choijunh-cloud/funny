"""산식 검증이 실패 없이 끝나는지."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oct2_brief import build as build_brief  # noqa: E402
from oct2_core import build as build_core  # noqa: E402
from oct2_verify import verify  # noqa: E402


class Oct2VerifyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build_core()
        build_brief()
        cls.report = verify()

    def test_no_arithmetic_failures(self):
        fails = [row for row in self.report["checks"] if row["status"] == "fail"]
        self.assertEqual(fails, [], fails)
        self.assertGreaterEqual(self.report["pass"], 12)
        self.assertTrue(self.report["ok"])

    def test_known_approximations_stay_notes(self):
        notes = {row["id"] for row in self.report["checks"] if row["status"] == "note"}
        self.assertIn("micron_capex_floor", notes)
        self.assertIn("hana_nine_percent", notes)
        self.assertIn("ten_year_range", notes)


if __name__ == "__main__":
    unittest.main()
