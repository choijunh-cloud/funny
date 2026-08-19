"""리포트용 인라인 SVG 차트 모듈.

외부 라이브러리·CDN 없이 문자열로 SVG를 만든다. 생성된 마크업을 HTML에 그대로
삽입하면 오프라인·인쇄(PDF) 환경에서도 동일하게 렌더링된다.
"""

from __future__ import annotations

from html import escape
from typing import Iterable, Sequence

NAVY = "#0f2043"
BLUE = "#1e407c"
SKY = "#4a80c4"
PALE = "#a9c3e4"
GOLD = "#b8943a"
RED = "#c0392b"
ROSE = "#e08b84"
GREEN = "#1f8a4c"
MINT = "#7fc2a0"
AMBER = "#d98c1f"
GRAY = "#6b7684"
LINE = "#d7dee8"
BG = "#f6f8fc"
INK = "#1a2230"

FS_TITLE = 15
FS_LABEL = 13
FS_VALUE = 13
FS_NOTE = 11.5


def _t(x, y, s, size=FS_LABEL, anchor="start", fill=INK, weight="normal", opacity=1.0):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
        f'fill="{fill}" font-weight="{weight}" opacity="{opacity}">{escape(str(s))}</text>'
    )


def _rect(x, y, w, h, fill, rx=3, opacity=1.0, stroke=None, sw=1):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" '
        f'rx="{rx}" fill="{fill}" opacity="{opacity}"{st}/>'
    )


def _line(x1, y1, x2, y2, color=LINE, w=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{w}"{d}/>'
    )


def _wrap(text: str, per_line: int) -> list[str]:
    """공백 기준 단순 줄바꿈. 한글은 글자수 기준으로 근사."""
    words = str(text).split()
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) > per_line and cur:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines or [""]


def _svg(w, h, body, cls="chart"):
    return (
        f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" role="img" '
        f'xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    )


def _fmt(v, dec=1, plus=False):
    s = f"{v:,.{dec}f}" if dec else f"{v:,.0f}"
    if plus and v > 0:
        s = "+" + s
    return s


def _arrow_defs():
    return (
        '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker>'
        '<marker id="arg" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{GOLD}"/></marker></defs>'
    )


# ---------------------------------------------------------------- 가로 막대


def bar_h(
    items: Sequence[tuple],
    unit: str = "%",
    label_w: int = 210,
    row: int = 30,
    dec: int = 1,
    width: int = 940,
    max_abs: float | None = None,
    pos_color: str = RED,
    neg_color: str = BLUE,
    show_zero_label: bool = True,
):
    """(라벨, 값[, 색][, 주석]) 목록을 좌우 발산형 가로 막대로 그린다."""
    pad_r, top = 78, 18
    plot_w = width - label_w - pad_r
    vals = [it[1] for it in items]
    mx = max_abs or max(abs(v) for v in vals) or 1
    mx *= 1.04
    has_neg, has_pos = min(vals) < 0, max(vals) > 0
    if has_neg and has_pos:
        zero_x, scale = label_w + plot_w / 2, (plot_w / 2) / mx
    elif has_neg:
        zero_x, scale = label_w + plot_w, plot_w / mx
    else:
        zero_x, scale = label_w, plot_w / mx

    h = top + row * len(items) + 12
    b = [_rect(label_w, top - 6, plot_w, row * len(items) + 4, BG, rx=4)]
    for i, it in enumerate(items):
        label, v = it[0], it[1]
        color = it[2] if len(it) > 2 and it[2] else (pos_color if v >= 0 else neg_color)
        note = it[3] if len(it) > 3 else ""
        y = top + i * row
        bh = row - 11
        w = abs(v) * scale
        x = zero_x if v >= 0 else zero_x - w
        b.append(_rect(x, y, w, bh, color, rx=2))
        b.append(_t(label_w - 10, y + bh - 3, label, anchor="end", size=FS_LABEL))
        if v >= 0:
            tx, anchor = x + w + 7, "start"
        elif not has_pos:
            # 전 종목 하락 차트: 값 라벨을 0선 오른쪽에 두어 축 라벨과 겹치지 않게 한다.
            tx, anchor = zero_x + 8, "start"
        else:
            tx, anchor = x - 7, "end"
        b.append(
            _t(
                tx,
                y + bh - 3,
                f"{_fmt(v, dec, plus=True)}{unit}",
                anchor=anchor,
                size=FS_VALUE,
                weight="bold",
                fill=color,
            )
        )
        if note:
            b.append(_t(width - 4, y + bh - 3, note, anchor="end", size=FS_NOTE, fill=GRAY))
    b.append(_line(zero_x, top - 6, zero_x, top + row * len(items) - 2, GRAY, 1))
    if show_zero_label and has_neg and has_pos:
        b.append(_t(zero_x, top - 10, "0", anchor="middle", size=FS_NOTE, fill=GRAY))
    return _svg(width, h, "".join(b))


# ---------------------------------------------------------------- 세로 그룹 막대


def bar_v_group(
    cats: Sequence[str],
    series: Sequence[dict],
    unit: str = "",
    width: int = 940,
    height: int = 330,
    dec: int = 1,
    y_max: float | None = None,
    legend: bool = True,
    cat_notes: Sequence[str] | None = None,
    bands: Sequence[tuple] | None = None,
):
    """series = [{"name":, "values":[...], "color":}] 형태의 그룹 막대."""
    pad_l, pad_r = 54, 20
    top = 34 if legend else 16
    bottom = 52 if cat_notes else 34
    plot_w = width - pad_l - pad_r
    plot_h = height - top - bottom
    nums = [v for s in series for v in s["values"] if v is not None]
    raw_hi = y_max if y_max is not None else (max(nums) if nums else 1)
    raw_lo = min(0, min(nums) if nums else 0)
    span = (raw_hi - raw_lo) or 1
    vmax = raw_hi + span * 0.18
    vmin = raw_lo - (span * 0.08 if raw_lo < 0 else 0)
    axis_span = (vmax - vmin) or 1

    def Y(v):
        return top + plot_h * (1 - (v - vmin) / axis_span)

    b = [_rect(pad_l, top, plot_w, plot_h, BG, rx=4)]

    for band in bands or []:
        lo, hi, color, txt = band
        y1, y2 = Y(hi), Y(lo)
        b.append(_rect(pad_l, y1, plot_w, y2 - y1, color, rx=0, opacity=0.16))
        b.append(_t(pad_l + 8, y1 + 14, txt, size=FS_NOTE, fill=GRAY))

    for k in range(5):
        gv = vmin + axis_span * k / 4
        y = Y(gv)
        b.append(_line(pad_l, y, pad_l + plot_w, y, LINE, 1))
        b.append(_t(pad_l - 8, y + 4, _fmt(gv, dec if abs(vmax) < 20 else 0), size=FS_NOTE, anchor="end", fill=GRAY))

    zero_y = Y(0)
    n_cat, n_ser = len(cats), len(series)
    slot = plot_w / n_cat
    gap = slot * 0.24
    bw = (slot - gap) / n_ser
    for ci, cat in enumerate(cats):
        cx = pad_l + slot * ci
        for si, s in enumerate(series):
            v = s["values"][ci]
            if v is None:
                continue
            y_top, y_bot = (Y(v), zero_y) if v >= 0 else (zero_y, Y(v))
            x = cx + gap / 2 + bw * si
            b.append(_rect(x, y_top, bw, max(y_bot - y_top, 2), s["color"], rx=2))
            lab_y = y_top - 6 if v >= 0 else y_bot + 14
            b.append(
                _t(x + bw / 2, lab_y, f"{_fmt(v, dec)}{unit}", anchor="middle", size=FS_VALUE, weight="bold", fill=s["color"])
            )
        b.append(_t(cx + slot / 2, top + plot_h + 19, cat, anchor="middle", size=FS_LABEL, weight="bold"))
        if cat_notes and cat_notes[ci]:
            b.append(_t(cx + slot / 2, top + plot_h + 37, cat_notes[ci], anchor="middle", size=FS_NOTE, fill=GRAY))

    if legend:
        lx = pad_l
        for s in series:
            b.append(_rect(lx, 10, 13, 13, s["color"], rx=2))
            b.append(_t(lx + 18, 21, s["name"], size=FS_NOTE))
            lx += 24 + len(s["name"]) * 8.4
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 수준·임계선


def threshold_scale(
    markers: Sequence[tuple],
    bands: Sequence[tuple],
    lo: float,
    hi: float,
    unit: str = "%",
    width: int = 940,
    dec: int = 2,
    axis_label: str = "",
):
    """구간 색상 밴드 위에 현재 수치를 찍는 수평 스케일.

    markers: (값, 라벨, 위/아래 offset 단계)
    bands:   (시작, 끝, 색, 구간명)
    """
    pad_l, pad_r = 20, 20
    axis_y = 150
    plot_w = width - pad_l - pad_r
    height = 218

    def X(v):
        return pad_l + plot_w * (v - lo) / (hi - lo)

    b = [_arrow_defs()]
    for s, e, color, txt in bands:
        x1, x2 = X(max(s, lo)), X(min(e, hi))
        b.append(_rect(x1, axis_y, x2 - x1, 26, color, rx=0, opacity=0.75))
        b.append(_t((x1 + x2) / 2, axis_y + 44, txt, anchor="middle", size=FS_NOTE, fill=GRAY))
    b.append(_rect(pad_l, axis_y, plot_w, 26, "none", rx=0, stroke="#ffffff", sw=0))

    ticks = 6
    for k in range(ticks + 1):
        v = lo + (hi - lo) * k / ticks
        x = X(v)
        b.append(_line(x, axis_y, x, axis_y + 32, "#ffffff", 1))
        b.append(_t(x, axis_y + 22 - 30, "", size=FS_NOTE))
        b.append(_t(x, axis_y + 76, f"{_fmt(v, dec)}{unit}", anchor="middle", size=FS_NOTE, fill=GRAY))

    for v, label, lvl in markers:
        x = X(v)
        y = axis_y - 22 - 42 * lvl
        b.append(_line(x, y + 6, x, axis_y - 2, NAVY, 1.6, dash="3 3"))
        b.append(f'<circle cx="{x:.1f}" cy="{axis_y + 13:.1f}" r="5.5" fill="{NAVY}"/>')
        tw = max(len(label) * 8.6, 60)
        bx = min(max(x - tw / 2, pad_l), width - pad_r - tw)
        b.append(_rect(bx, y - 15, tw, 22, "#ffffff", rx=4, stroke=NAVY, sw=1.2))
        b.append(_t(bx + tw / 2, y + 1, label, anchor="middle", size=FS_NOTE, weight="bold", fill=NAVY))
    if axis_label:
        b.append(_t(pad_l, 22, axis_label, size=FS_TITLE, weight="bold", fill=NAVY))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 워터폴


def waterfall(steps: Sequence[tuple], unit: str = "조원", width: int = 940, height: int = 340, dec: int = 1):
    """steps: (라벨, 값, 종류) — 종류: base|plus|minus|total."""
    pad_l, pad_r, top, bottom = 56, 20, 26, 62
    plot_w = width - pad_l - pad_r
    plot_h = height - top - bottom

    run = 0.0
    bars = []
    peak = 0.0
    for label, v, kind in steps:
        if kind in ("base", "total"):
            start, end = 0.0, v
        elif kind == "minus":
            start, end = run - abs(v), run
            start, end = run, run - abs(v)
        else:
            start, end = run, run + v
        bars.append((label, start, end, kind, v))
        run = end
        peak = max(peak, abs(start), abs(end))
    vmax = peak * 1.2 or 1

    def Y(v):
        return top + plot_h * (1 - v / vmax)

    b = [_rect(pad_l, top, plot_w, plot_h, BG, rx=4)]
    for k in range(5):
        y = top + plot_h * (1 - k / 4)
        b.append(_line(pad_l, y, pad_l + plot_w, y, LINE, 1))
        b.append(_t(pad_l - 8, y + 4, _fmt(vmax * k / 4, 0), anchor="end", size=FS_NOTE, fill=GRAY))

    slot = plot_w / len(bars)
    bw = slot * 0.54
    colors = {"base": NAVY, "total": BLUE, "plus": GREEN, "minus": GOLD}
    prev_x2 = None
    for i, (label, start, end, kind, v) in enumerate(bars):
        cx = pad_l + slot * i + slot / 2
        x = cx - bw / 2
        y1, y2 = Y(max(start, end)), Y(min(start, end))
        b.append(_rect(x, y1, bw, max(y2 - y1, 2), colors[kind], rx=2))
        vlabel = f"{_fmt(abs(v), dec)}{unit}" if kind != "minus" else f"-{_fmt(abs(v), dec)}{unit}"
        b.append(_t(cx, y1 - 8, vlabel, anchor="middle", size=FS_VALUE, weight="bold", fill=colors[kind]))
        for li, ln in enumerate(_wrap(label, 12)):
            b.append(_t(cx, top + plot_h + 20 + li * 15, ln, anchor="middle", size=FS_NOTE))
        if prev_x2 is not None:
            b.append(_line(prev_x2, Y(start), x, Y(start), GRAY, 1, dash="3 3"))
        prev_x2 = x + bw
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 인과 체인


def chain_h(nodes: Sequence[tuple], width: int = 940, per_line: int = 9, tone_map: dict | None = None):
    """가로 인과 체인. nodes: (텍스트, 톤) 톤: key|bad|good|neutral."""
    tones = tone_map or {"key": NAVY, "bad": RED, "good": GREEN, "neutral": BLUE, "warn": AMBER}
    n = len(nodes)
    gap = 26
    bw = (width - gap * (n - 1) - 8) / n
    lines_max = max(len(_wrap(t[0], per_line)) for t in nodes)
    bh = 30 + lines_max * 17
    height = bh + 20
    b = [_arrow_defs()]
    for i, (txt, tone) in enumerate(nodes):
        color = tones.get(tone, BLUE)
        x = 4 + i * (bw + gap)
        b.append(_rect(x, 10, bw, bh, color, rx=6, opacity=0.12))
        b.append(_rect(x, 10, 4, bh, color, rx=2))
        wl = _wrap(txt, per_line)
        y0 = 10 + bh / 2 - (len(wl) - 1) * 8.5
        for li, ln in enumerate(wl):
            b.append(_t(x + bw / 2 + 2, y0 + li * 17 + 5, ln, anchor="middle", size=FS_LABEL, weight="bold", fill=color))
        if i < n - 1:
            ax = x + bw + 4
            b.append(_line(ax, 10 + bh / 2, ax + gap - 8, 10 + bh / 2, GRAY, 1.6) .replace("/>", ' marker-end="url(#ar)"/>'))
    return _svg(width, height, "".join(b))


def chain_v(nodes: Sequence[tuple], width: int = 520, node_w: int = 380, per_line: int = 26):
    """세로 인과 체인. nodes: (텍스트, 톤[, 우측주석])."""
    tones = {"key": NAVY, "bad": RED, "good": GREEN, "neutral": BLUE, "warn": AMBER}
    ys, b = 8, [_arrow_defs()]
    x = 10
    for i, node in enumerate(nodes):
        txt, tone = node[0], node[1]
        note = node[2] if len(node) > 2 else ""
        color = tones.get(tone, BLUE)
        wl = _wrap(txt, per_line)
        bh = 16 + len(wl) * 18
        b.append(_rect(x, ys, node_w, bh, color, rx=6, opacity=0.12))
        b.append(_rect(x, ys, 4, bh, color, rx=2))
        for li, ln in enumerate(wl):
            b.append(_t(x + 16, ys + 22 + li * 18, ln, size=FS_LABEL, weight="bold", fill=color))
        if note:
            b.append(_t(x + node_w + 14, ys + bh / 2 + 5, note, size=FS_NOTE, fill=GRAY))
        ys += bh
        if i < len(nodes) - 1:
            b.append(_line(x + node_w / 2, ys + 2, x + node_w / 2, ys + 20, GRAY, 1.6).replace("/>", ' marker-end="url(#ar)"/>'))
            ys += 24
    return _svg(width, ys + 10, "".join(b))


# ---------------------------------------------------------------- 2x2 매트릭스


def quad_matrix(
    x_axis: tuple,
    y_axis: tuple,
    cells: Sequence[tuple],
    width: int = 940,
    height: int = 400,
):
    """cells: 4개 (제목, 본문, 톤) — 순서: 좌상, 우상, 좌하, 우하."""
    tones = {"good": GREEN, "bad": RED, "warn": AMBER, "neutral": BLUE}
    pad_l, pad_b, top, pad_r = 96, 62, 20, 20
    pw, ph = width - pad_l - pad_r, height - top - pad_b
    cw, ch = pw / 2, ph / 2
    b = []
    for idx, (title, body, tone) in enumerate(cells):
        col, rowi = idx % 2, idx // 2
        x, y = pad_l + col * cw, top + rowi * ch
        color = tones.get(tone, BLUE)
        b.append(_rect(x + 4, y + 4, cw - 8, ch - 8, color, rx=8, opacity=0.10))
        b.append(_t(x + 20, y + 32, title, size=FS_TITLE, weight="bold", fill=color))
        for li, ln in enumerate(_wrap(body, 26)):
            b.append(_t(x + 20, y + 56 + li * 18, ln, size=FS_NOTE, fill=INK))
    b.append(_line(pad_l, top, pad_l, top + ph, GRAY, 1.4))
    b.append(_line(pad_l, top + ph, pad_l + pw, top + ph, GRAY, 1.4))
    b.append(_t(pad_l + pw / 2, height - 30, x_axis[0], anchor="middle", size=FS_LABEL, weight="bold", fill=NAVY))
    b.append(_t(pad_l + 6, height - 12, x_axis[1], size=FS_NOTE, fill=GRAY))
    b.append(_t(pad_l + pw - 6, height - 12, x_axis[2], anchor="end", size=FS_NOTE, fill=GRAY))
    b.append(
        f'<text transform="translate(28,{top + ph / 2:.1f}) rotate(-90)" text-anchor="middle" '
        f'font-size="{FS_LABEL}" font-weight="bold" fill="{NAVY}">{escape(y_axis[0])}</text>'
    )
    b.append(_t(52, top + 14, y_axis[1], size=FS_NOTE, fill=GRAY))
    b.append(_t(52, top + ph - 4, y_axis[2], size=FS_NOTE, fill=GRAY))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 도넛


def donut(pct: float, center: str, sub: str = "", width: int = 250, color: str = GOLD, dec: int = 1):
    r, cx, cy, sw = 78, width / 2, 118, 24
    circ = 2 * 3.141592653589793 * r
    dash = circ * min(pct, 100) / 100
    b = [
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BG}" stroke-width="{sw}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{sw}" '
        f'stroke-dasharray="{dash:.2f} {circ - dash:.2f}" stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/>',
        _t(cx, cy + 4, center, anchor="middle", size=24, weight="bold", fill=NAVY),
        _t(cx, cy + 28, sub, anchor="middle", size=FS_NOTE, fill=GRAY),
    ]
    return _svg(width, 220, "".join(b))


# ---------------------------------------------------------------- 선 차트


def line_chart(
    x_labels: Sequence[str],
    series: Sequence[dict],
    width: int = 940,
    height: int = 330,
    unit: str = "",
    y_min: float | None = None,
    y_max: float | None = None,
    dec: int = 1,
    point_labels: bool = True,
):
    pad_l, pad_r, top, bottom = 56, 96, 34, 42
    pw, ph = width - pad_l - pad_r, height - top - bottom
    allv = [v for s in series for v in s["values"]]
    vmin = y_min if y_min is not None else min(allv) * 0.96
    vmax = y_max if y_max is not None else max(allv) * 1.04
    b = [_rect(pad_l, top, pw, ph, BG, rx=4)]
    for k in range(5):
        y = top + ph * (1 - k / 4)
        b.append(_line(pad_l, y, pad_l + pw, y, LINE, 1))
        b.append(_t(pad_l - 8, y + 4, _fmt(vmin + (vmax - vmin) * k / 4, dec), anchor="end", size=FS_NOTE, fill=GRAY))
    n = len(x_labels)
    xs = [pad_l + (pw / (n - 1)) * i for i in range(n)] if n > 1 else [pad_l + pw / 2]
    for i, lb in enumerate(x_labels):
        b.append(_t(xs[i], top + ph + 22, lb, anchor="middle", size=FS_LABEL, weight="bold"))
    for s in series:
        pts = []
        for i, v in enumerate(s["values"]):
            y = top + ph * (1 - (v - vmin) / (vmax - vmin))
            pts.append((xs[i], y))
        d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
        b.append(f'<path d="{d}" fill="none" stroke="{s["color"]}" stroke-width="2.6"/>')
        for i, (x, y) in enumerate(pts):
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="#fff" stroke="{s["color"]}" stroke-width="2.4"/>')
            if point_labels:
                b.append(
                    _t(x, y - 12, f"{_fmt(s['values'][i], dec)}{unit}", anchor="middle", size=FS_NOTE, weight="bold", fill=s["color"])
                )
        b.append(_t(pts[-1][0] + 12, pts[-1][1] + 4, s["name"], size=FS_NOTE, weight="bold", fill=s["color"]))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 진행률 막대


def progress_bars(rows: Sequence[tuple], max_pct: float = 100, unit: str = "%", width: int = 940, label_w: int = 210, dec: int = 0):
    """rows: (라벨, 값, 색[, 주석]) — 트랙 위에 채움 막대."""
    row_h, top = 40, 12
    pad_r = 200
    track_w = width - label_w - pad_r
    height = top + row_h * len(rows) + 8
    b = []
    for i, r in enumerate(rows):
        label, v, color = r[0], r[1], r[2]
        note = r[3] if len(r) > 3 else ""
        y = top + i * row_h
        b.append(_rect(label_w, y, track_w, 24, BG, rx=4))
        b.append(_rect(label_w, y, track_w * min(v / max_pct, 1), 24, color, rx=4))
        b.append(_t(label_w - 12, y + 17, label, anchor="end", size=FS_LABEL, weight="bold"))
        b.append(
            _t(label_w + track_w + 10, y + 17, f"{_fmt(v, dec)}{unit}", size=FS_VALUE, weight="bold", fill=color)
        )
        if note:
            b.append(_t(label_w + track_w + 74, y + 17, note, size=FS_NOTE, fill=GRAY))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 로드맵


def roadmap(items: Sequence[tuple], unit: str = "억원", width: int = 940, height: int = 300, dec: int = 0):
    """items: (시점, 값, 주석) — 우상향 계단 막대."""
    pad_l, pad_r, top, bottom = 20, 20, 34, 62
    pw, ph = width - pad_l - pad_r, height - top - bottom
    vmax = max(v for _, v, _ in items) * 1.25
    slot = pw / len(items)
    bw = slot * 0.42
    b = [_arrow_defs()]
    prev = None
    for i, (when, v, note) in enumerate(items):
        cx = pad_l + slot * i + slot / 2
        bh = ph * v / vmax
        y = top + ph - bh
        color = [PALE, SKY, BLUE, NAVY][min(i, 3)]
        b.append(_rect(cx - bw / 2, y, bw, bh, color, rx=4))
        b.append(_t(cx, y - 10, f"{_fmt(v, dec)}{unit}", anchor="middle", size=FS_TITLE, weight="bold", fill=NAVY))
        b.append(_t(cx, top + ph + 22, when, anchor="middle", size=FS_LABEL, weight="bold"))
        for li, ln in enumerate(_wrap(note, 22)):
            b.append(_t(cx, top + ph + 40 + li * 15, ln, anchor="middle", size=FS_NOTE, fill=GRAY))
        if prev is not None:
            b.append(_line(prev[0], prev[1], cx - bw / 2 - 6, y + 8, GOLD, 1.8, dash="4 3").replace("/>", ' marker-end="url(#arg)"/>'))
        prev = (cx + bw / 2 + 6, y + 8)
    b.append(_line(pad_l, top + ph, pad_l + pw, top + ph, GRAY, 1.2))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 구간(레인지) 막대


def range_bars(
    items: Sequence[tuple],
    lo: float,
    hi: float,
    unit: str = "만원",
    width: int = 940,
    label_w: int = 250,
    dec: int = 0,
    ref: tuple | None = None,
):
    """items: (라벨, 하단, 상단, 색[, 주석]) — 공통 축 위 구간 표시. ref: (값, 라벨)."""
    pad_r, top, row_h = 30, 46, 44
    pw = width - label_w - pad_r
    height = top + row_h * len(items) + 44

    def X(v):
        return label_w + pw * (v - lo) / (hi - lo)

    b = [_rect(label_w, top - 10, pw, row_h * len(items) + 6, BG, rx=4)]
    for k in range(6):
        v = lo + (hi - lo) * k / 5
        x = X(v)
        b.append(_line(x, top - 10, x, top + row_h * len(items) - 4, LINE, 1))
        b.append(_t(x, top + row_h * len(items) + 14, f"{_fmt(v, dec)}", anchor="middle", size=FS_NOTE, fill=GRAY))
    if ref:
        rx_ = X(ref[0])
        b.append(_line(rx_, top - 22, rx_, top + row_h * len(items) - 4, NAVY, 1.8, dash="5 3"))
        b.append(_t(rx_, top - 28, ref[1], anchor="middle", size=FS_NOTE, weight="bold", fill=NAVY))
    for i, it in enumerate(items):
        label, v1, v2, color = it[0], it[1], it[2], it[3]
        note = it[4] if len(it) > 4 else ""
        y = top + i * row_h
        x1, x2 = X(min(v1, v2)), X(max(v1, v2))
        if x2 - x1 < 6:
            b.append(f'<circle cx="{x1:.1f}" cy="{y + 11:.1f}" r="7" fill="{color}"/>')
            txt = f"{_fmt(v1, dec)}{unit}"
        else:
            b.append(_rect(x1, y, x2 - x1, 22, color, rx=11, opacity=0.9))
            txt = f"{_fmt(min(v1, v2), dec)}~{_fmt(max(v1, v2), dec)}{unit}"
        b.append(_t(label_w - 12, y + 16, label, anchor="end", size=FS_LABEL, weight="bold"))
        b.append(_t(max(x2 + 10, x1 + 16), y + 16, txt, size=FS_VALUE, weight="bold", fill=color))
        if note:
            b.append(_t(label_w - 12, y + 32, note, anchor="end", size=FS_NOTE, fill=GRAY))
    b.append(_t(label_w, 18, f"단위: {unit}", size=FS_NOTE, fill=GRAY))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 타임라인


def timeline(events: Sequence[tuple], start_h: float = 6, end_h: float = 24, width: int = 940):
    """events: ("HH:MM", 텍스트, 톤) — 하루 흐름 축."""
    tones = {"key": NAVY, "bad": RED, "good": GREEN, "warn": AMBER, "neutral": BLUE}
    pad_l, pad_r = 26, 26
    pw = width - pad_l - pad_r
    axis_y = 168
    height = 330
    b = [_line(pad_l, axis_y, pad_l + pw, axis_y, GRAY, 2)]
    for h in range(int(start_h), int(end_h) + 1, 2):
        x = pad_l + pw * (h - start_h) / (end_h - start_h)
        b.append(_line(x, axis_y - 5, x, axis_y + 5, GRAY, 1.4))
        b.append(_t(x, axis_y + 22, f"{h:02d}시", anchor="middle", size=FS_NOTE, fill=GRAY))

    slots_up, slots_dn = [], []
    for tstr, txt, tone in events:
        hh, mm = (int(p) for p in tstr.split(":"))
        val = hh + mm / 60
        x = pad_l + pw * (val - start_h) / (end_h - start_h)
        color = tones.get(tone, BLUE)
        up = len(slots_up) <= len(slots_dn)
        lane = len(slots_up) if up else len(slots_dn)
        (slots_up if up else slots_dn).append(x)
        wl = _wrap(txt, 15)
        bh = 20 + len(wl) * 16
        bwid = 150
        bx = min(max(x - bwid / 2, pad_l), pad_l + pw - bwid)
        if up:
            by = axis_y - 26 - bh - (lane % 2) * 4
        else:
            by = axis_y + 36 + (lane % 2) * 4
        b.append(_line(x, axis_y, x, by + (bh if not up else 0) + (0 if up else -6), color, 1.2, dash="3 2"))
        b.append(f'<circle cx="{x:.1f}" cy="{axis_y:.1f}" r="5" fill="{color}"/>')
        b.append(_rect(bx, by, bwid, bh, color, rx=5, opacity=0.12))
        b.append(_t(bx + 8, by + 15, tstr, size=FS_NOTE, weight="bold", fill=color))
        for li, ln in enumerate(wl):
            b.append(_t(bx + 8, by + 15 + (li + 1) * 15, ln, size=FS_NOTE, fill=INK))
    return _svg(width, height, "".join(b))


# ---------------------------------------------------------------- 스코어보드 타일


def tiles(items: Sequence[tuple], width: int = 940, cols: int = 4):
    """items: (제목, 값, 변화문구, 톤)."""
    tones = {"good": GREEN, "bad": RED, "warn": AMBER, "neutral": BLUE, "key": NAVY}
    gap = 14
    tw = (width - gap * (cols - 1)) / cols
    th = 96
    rows = (len(items) + cols - 1) // cols
    height = rows * (th + gap)
    b = []
    for i, (title, value, delta, tone) in enumerate(items):
        color = tones.get(tone, BLUE)
        x = (i % cols) * (tw + gap)
        y = (i // cols) * (th + gap)
        b.append(_rect(x, y, tw, th, color, rx=8, opacity=0.10))
        b.append(_rect(x, y, tw, 4, color, rx=2))
        b.append(_t(x + 14, y + 28, title, size=FS_NOTE, fill=GRAY))
        b.append(_t(x + 14, y + 58, value, size=21, weight="bold", fill=NAVY))
        b.append(_t(x + 14, y + 80, delta, size=FS_NOTE, weight="bold", fill=color))
    return _svg(width, height, "".join(b))
