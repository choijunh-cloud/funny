"""Quarterly cash purchases of property and equipment from SEC company facts.

Primary series is cash paid, not accruals and not finance-lease additions.
Microsoft's fiscal year ends in June; quarters are aligned on calendar quarter
ends. Amazon changed XBRL concepts in 2017, so 2016-2017 uses an explicit
bridge documented in `amazon_bridge`.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import requests

SEC_HEADERS = {"User-Agent": "capex-acceleration-research research@example.com"}

COMPANIES: dict[str, dict] = {
    "MSFT": {
        "cik": "0000789019",
        "tags": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    },
    "GOOGL": {
        "cik": "0001652044",
        "tags": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    },
    "AMZN": {
        "cik": "0001018724",
        "tags": ["PaymentsToAcquireProductiveAssets", "PaymentsToAcquirePropertyPlantAndEquipment"],
    },
    "META": {
        "cik": "0001326801",
        "tags": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    },
}

FORMS = {"10-Q", "10-K", "10-Q/A", "10-K/A"}
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def calendar_quarter_end(d: date) -> date:
    quarter = (d.month - 1) // 3
    month, day = [(3, 31), (6, 30), (9, 30), (12, 31)][quarter]
    return date(d.year, month, day)


def fetch_companyfacts(cik: str, refresh: bool = False) -> dict:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"CIK{cik}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)
    return response.json()


def _facts(data: dict, tag: str) -> list[dict]:
    concept = data.get("facts", {}).get("us-gaap", {}).get(tag)
    if not concept:
        return []
    best: dict[tuple[str, str], dict] = {}
    for rec in concept["units"].get("USD", []):
        if rec.get("form") not in FORMS or "start" not in rec or "end" not in rec:
            continue
        key = (rec["start"], rec["end"])
        prev = best.get(key)
        if prev is None or rec.get("filed", "") >= prev.get("filed", ""):
            best[key] = rec
    return list(best.values())


def quarterly_from_tag(data: dict, tag: str) -> dict[date, float]:
    """Quarterly USD amounts. Direct ~90-day facts win. Else difference a YTD chain."""
    direct: dict[date, tuple[float, str]] = {}
    by_start: dict[date, dict[date, dict]] = defaultdict(dict)
    for rec in _facts(data, tag):
        start, end = _parse_date(rec["start"]), _parse_date(rec["end"])
        days = (end - start).days
        if days < 70:
            continue
        qe = calendar_quarter_end(end)
        if abs((end - qe).days) > 12:
            continue
        if 70 <= days <= 110:
            prev = direct.get(qe)
            if prev is None or rec["filed"] >= prev[1]:
                direct[qe] = (float(rec["val"]), rec["filed"])
        by_start[start][end] = rec

    derived: dict[date, tuple[float, str]] = {}
    for start, ends in by_start.items():
        prev_val = 0.0
        prev_end: date | None = None
        for end, rec in sorted(ends.items()):
            if prev_end is None and (end - start).days > 110:
                prev_val = float(rec["val"])
                prev_end = end
                continue
            if prev_end is not None and not 70 <= (end - prev_end).days <= 110:
                prev_val = float(rec["val"])
                prev_end = end
                continue
            qe = calendar_quarter_end(end)
            qval = float(rec["val"]) - prev_val
            prev = derived.get(qe)
            if prev is None or rec["filed"] >= prev[1]:
                derived[qe] = (qval, rec["filed"])
            prev_val = float(rec["val"])
            prev_end = end

    out: dict[date, float] = {}
    for qe in set(direct) | set(derived):
        out[qe] = direct[qe][0] if qe in direct else derived[qe][0]
    return out


def _duration_value(data: dict, tag: str, start: date, end: date, lo: int, hi: int) -> float | None:
    matches = []
    for rec in _facts(data, tag):
        s, e = _parse_date(rec["start"]), _parse_date(rec["end"])
        days = (e - s).days
        if s == start and e == end and lo <= days <= hi:
            matches.append(rec)
    if not matches:
        return None
    matches.sort(key=lambda rec: rec.get("filed", ""))
    return float(matches[-1]["val"])


def amazon_bridge(data: dict, quarterly: dict[date, float]) -> dict[date, float]:
    """Fill 2016-2017 so the modern 'productive assets' concept is continuous.

    From 2018 onward Amazon files PaymentsToAcquireProductiveAssets quarterly.
    Fiscal 2017 has a 9-month YTD and a Q3 fact, but not separate Q1/Q2 gross
    amounts. Q1/Q2 are split with the restated net-capex ratio from
    PaymentsForProceedsFromProductiveAssets. Fiscal 2016 quarterly shape comes
    from the older PPE tag, scaled to the restated 2016 annual total.
    """
    out = dict(quarterly)
    gross = "PaymentsToAcquireProductiveAssets"
    old = "PaymentsToAcquirePropertyPlantAndEquipment"
    net = "PaymentsForProceedsFromProductiveAssets"

    fy2016 = _duration_value(data, gross, date(2016, 1, 1), date(2016, 12, 31), 350, 380)
    fy2017 = _duration_value(data, gross, date(2017, 1, 1), date(2017, 12, 31), 350, 380)
    nine_m = _duration_value(data, gross, date(2017, 1, 1), date(2017, 9, 30), 260, 290)
    q3 = _duration_value(data, gross, date(2017, 7, 1), date(2017, 9, 30), 80, 100)
    net_h1 = _duration_value(data, net, date(2017, 1, 1), date(2017, 6, 30), 170, 200)
    net_q2 = _duration_value(data, net, date(2017, 4, 1), date(2017, 6, 30), 80, 100)
    old_fy = _duration_value(data, old, date(2016, 1, 1), date(2016, 12, 31), 350, 380)
    if None in (fy2016, fy2017, nine_m, q3, net_h1, net_q2, old_fy):
        raise RuntimeError("Amazon 2016-2017 bridge facts are missing")

    h1_gross = nine_m - q3
    q2 = h1_gross * (net_q2 / net_h1)
    q1 = h1_gross - q2
    q4 = fy2017 - nine_m
    out[date(2017, 3, 31)] = q1
    out[date(2017, 6, 30)] = q2
    out[date(2017, 9, 30)] = q3
    out[date(2017, 12, 31)] = q4

    old_q = quarterly_from_tag(data, old)
    old_parts = [old_q.get(date(2016, m, d)) for m, d in ((3, 31), (6, 30), (9, 30), (12, 31))]
    if any(v is None for v in old_parts):
        # Q4 of the old tag is often only the annual residual.
        q1_old, q2_old, q3_old = old_parts[:3]
        if None in (q1_old, q2_old, q3_old):
            raise RuntimeError("Amazon 2016 old-tag quarters are missing")
        old_parts[3] = old_fy - (q1_old + q2_old + q3_old)
    scale = fy2016 / old_fy
    for qe, value in zip(
        [date(2016, 3, 31), date(2016, 6, 30), date(2016, 9, 30), date(2016, 12, 31)],
        old_parts,
    ):
        out[qe] = value * scale
    return out


def splice_tags(data: dict, tags: list[str]) -> dict[date, float]:
    """Older concepts fill gaps. Newer concepts overwrite on overlap."""
    merged: dict[date, float] = {}
    for tag in reversed(tags):
        merged.update(quarterly_from_tag(data, tag))
    return merged


def load_company_quarters(refresh: bool = False) -> dict[str, dict[date, float]]:
    series: dict[str, dict[date, float]] = {}
    for name, spec in COMPANIES.items():
        data = fetch_companyfacts(spec["cik"], refresh=refresh)
        quarterly = splice_tags(data, spec["tags"])
        if name == "AMZN":
            quarterly = amazon_bridge(data, quarterly)
        series[name] = quarterly
    return series


def combined_cash(
    series: dict[str, dict[date, float]],
    start: date = date(2016, 3, 31),
    end: date = date(2026, 6, 30),
) -> tuple[list[date], list[float], dict[date, dict[str, float]]]:
    from capex_accel.metrics import add_quarters

    quarters: list[date] = []
    qe = start
    while qe <= end:
        quarters.append(qe)
        qe = add_quarters(qe, 1)
    missing = [
        f"{name} {qe.isoformat()}"
        for qe in quarters
        for name in COMPANIES
        if qe not in series[name]
    ]
    if missing:
        raise RuntimeError("missing quarters: " + ", ".join(missing[:12]))
    by_q: dict[date, dict[str, float]] = {}
    totals: list[float] = []
    for qe in quarters:
        parts = {name: series[name][qe] / 1e9 for name in COMPANIES}
        by_q[qe] = parts
        totals.append(sum(parts.values()))
    return quarters, totals, by_q


def annual_sums(by_q: dict[date, dict[str, float]], year: int) -> dict[str, float]:
    ends = [date(year, 3, 31), date(year, 6, 30), date(year, 9, 30), date(year, 12, 31)]
    out = {}
    for name in COMPANIES:
        out[name] = sum(by_q[qe][name] for qe in ends)
    out["TOTAL"] = sum(out[name] for name in COMPANIES)
    return out
