"""CLI and report writer smoke tests."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CliTests(unittest.TestCase):
    def test_module_writes_report_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
            proc = subprocess.run(
                [sys.executable, "-m", "hybrid_synthesis", "--all-scenarios", "--out", tmp],
                cwd=ROOT,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            out = Path(tmp)
            html = out / "2026-09-03-hybrid-synthesis.html"
            js = out / "2026-09-03-hybrid-synthesis.json"
            md = out / "VIEW_THIS_REPORT.md"
            self.assertTrue(html.is_file(), proc.stdout)
            self.assertTrue(js.is_file())
            self.assertTrue(md.is_file())
            payload = json.loads(js.read_text(encoding="utf-8"))
            tickers = [row["ticker"] for row in payload["portfolio"]["holdings"]]
            self.assertIn("005930", tickers)
            self.assertIn("000660", tickers)
            self.assertNotIn("222800", tickers)
            html_text = html.read_text(encoding="utf-8")
            self.assertIn("M = (매크로 압박 해소율 R)", html_text)
            self.assertIn("삼성전자", html_text)
            self.assertIn("ranking", payload)
            self.assertEqual(payload["ranking"]["top10"][0]["ticker"], "000660")
            self.assertNotIn("003160", [row["ticker"] for row in payload["ranking"]["top10"]])
            self.assertIn("하반기 KOSPI Top 10", html_text)
            self.assertIn("한국금융지주", html_text)


if __name__ == "__main__":
    unittest.main()
