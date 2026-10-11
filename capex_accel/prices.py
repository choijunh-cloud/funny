"""Split-adjusted daily closes from the Yahoo chart API."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}
CACHE = Path(__file__).resolve().parents[1] / "data" / "cache" / "prices.json"

TICKERS = {
    "NVDA": "NVDA",
    "MU": "MU",
    "AVGO": "AVGO",
    "TSM": "TSM",
    "SOX": "^SOX",
    "SK하이닉스": "000660.KS",
    "삼성전자": "005930.KS",
}


def fetch_prices(
    start: date = date(2014, 1, 1),
    end: date = date(2026, 10, 11),
    refresh: bool = False,
) -> dict[str, list[tuple[date, float]]]:
    if CACHE.exists() and not refresh:
        raw = json.loads(CACHE.read_text())
        return {name: [(date.fromisoformat(d), px) for d, px in rows] for name, rows in raw.items()}

    period1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    period2 = int(datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp())
    out: dict[str, list[tuple[date, float]]] = {}
    for name, symbol in TICKERS.items():
        url = (
            "https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{symbol}?period1={period1}&period2={period2}&interval=1d"
        )
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        result = response.json()["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        rows = []
        for ts, close in zip(result["timestamp"], closes):
            if close is None:
                continue
            rows.append((datetime.fromtimestamp(ts, timezone.utc).date(), float(close)))
        out[name] = rows
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(
        json.dumps({name: [(d.isoformat(), px) for d, px in rows] for name, rows in out.items()})
    )
    return out


def price_asof(rows: list[tuple[date, float]], day: date) -> tuple[date, float] | None:
    prev = None
    for d, px in rows:
        if d <= day:
            prev = (d, px)
        else:
            break
    return prev

