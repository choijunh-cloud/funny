"""텍스트 정규화와 OCR에서 반복되는 깨짐 보정."""

from __future__ import annotations

import re


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def snippet(text: str, start: int, end: int, pad: int = 90) -> str:
    left = max(0, start - pad)
    right = min(len(text), end + pad)
    return compact(text[left:right])[:240]


def normalize_keep_lines(text: str) -> str:
    text = text.replace("\u00a0", " ").replace("\u200b", "")
    text = text.replace("～", "~").replace("∼", "~").replace("－", "-")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def repair_ocr(text: str) -> str:
    """표 이미지 OCR에서 확인된 자리 깨짐만 고친다. 깨끗한 본문에는 쓰지 않는다."""
    text = re.sub(r"(20\d{2})\s*\n\s*년", r"\1년", text)
    text = re.sub(r"년\s*3596", "년 35%", text)
    text = re.sub(r"4196", "41%", text)
    text = re.sub(r"1396", "13%", text)
    text = re.sub(r"4Q\s*40%\s*배당", "4Q 40조 배당", text)
    text = re.sub(r"20274", "2027년", text)
    text = re.sub(r"명업이익", "영업이익", text)
    text = re.sub(r"30\s*30조", "3Q 30조", text)
    text = re.sub(r"709\s*전망", "70% 전망", text)
    text = re.sub(r"\$(\d{1,2})(?=\s|$)", r"+\1", text)
    rules = [
        (r"(\d)\s+(\d{2})(?=B\b)", r"\1.\2"),
        (r"\$(\d+),(\d{2})B", r"$\1.\2B"),
        (r"2026년\s*3596", "2026년 35%"),
        (r"309%6", "30%"),
        (r"704만주\s*\(1990\)", "704만주(19%)"),
        (r"비중\s*709", "비중 70%"),
        (r"10\\\s*\+", "+"),
        (r"\b40\s*DRAM", "4Q DRAM"),
        (r"\b30\s*DRAM", "3Q DRAM"),
        (r"\b40\s*NAND", "4Q NAND"),
        (r"\b30\s*NAND", "3Q NAND"),
        (r"NAND\s*\+\s*6\s*~\s*119\s*%", "NAND +6~11%"),
        (r"3Q보다\s*40\b", "3Q보다 4Q"),
        (r"FY26\s*40\b", "FY26 4Q"),
        (r"FY27\s*10\b", "FY27 1Q"),
        (r"Al\s*메모리", "AI 메모리"),
        (r"이자전지", "2차전지"),
        (r"면료전지", "2차전지"),
    ]
    for pattern, repl in rules:
        text = re.sub(pattern, repl, text)
    return text


def money_b_from_eok(raw: str) -> str:
    """억 달러를 십억 달러 표기로 바꾼다. 542.3억 달러 = $54.23B."""
    value = float(raw.replace(",", "")) / 10.0
    return money_b(value)


def money_b(value: float) -> str:
    rounded = round(value + 1e-9, 2)
    text = f"{rounded:.2f}".rstrip("0").rstrip(".")
    return f"${text}B"


def signed_pct(raw: str) -> str:
    number = raw.strip().lstrip("+")
    return f"+{number}%"


def split_bracket_sections(text: str) -> dict[str, str]:
    parts = re.split(r"\[([^\]]{2,40})\]", text)
    sections: dict[str, str] = {}
    if len(parts) < 3:
        return sections
    for index in range(1, len(parts) - 1, 2):
        sections[parts[index].strip()] = parts[index + 1]
    return sections
