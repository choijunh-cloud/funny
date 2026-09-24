#!/usr/bin/env python3
"""Recompute the 9-name 2027 EPS x PER Monte Carlo and compare with the published table.

Assumptions follow the written model, not a fitted probability of investment success.
Prices are 2026-09-23 KRX closes. Earnings are the 2026-09-24 FnGuide consensus
embedded in that write-up. Author PER, shock widths, and correlations are assumptions.
"""

from __future__ import annotations

from itertools import product

import numpy as np

# sales, op, ni: 억원. price, eps: 원.
# Groups: materials/consumables, substrate, equipment, socket.
ROWS = [
    ("솔브레인", "mat", 370_000, 14769, 2749, 2195, 28214, 0.10, 0.020, 0.78, 0.20, 17.0, 13.89, False),
    ("이수페타시스", "sub", 118_900, 22680, 5293, 4263, 5808, 0.18, 0.035, 0.78, 0.20, 25.0, 22.46, False),
    ("테스", "eq", 161_900, 6112, 1414, 1389, 7175, 0.20, 0.035, 0.78, 0.25, 25.0, 23.82, False),
    ("HPSP", "eq", 55_500, 3668, 2071, 1675, 2035, 0.18, 0.045, 0.78, 0.20, 30.0, 29.52, False),
    ("한솔케미칼", "mat", 236_500, 11340, 2276, 2038, 18884, 0.12, 0.022, 0.78, 0.20, 17.0, 13.38, False),
    ("심텍", "sub", 149_500, 25166, 4290, 3316, 8615, 0.20, 0.045, 0.78, 0.20, 20.0, 19.01, False),
    ("티씨케이", "mat", 286_000, 5036, 1669, 1383, 12366, 0.14, 0.025, 0.78, 0.20, 25.0, 24.52, False),
    ("피에스케이홀딩스", "eq", 163_200, 3884, 1567, 1879, 8713, 0.18, 0.040, 0.85, 0.25, 25.0, 19.97, True),
    ("ISC", "sock", 212_500, 4037, 1430, 1208, 5699, 0.20, 0.040, 0.78, 0.20, 30.0, 39.85, False),
]

PUBLISHED = [
    ("한솔케미칼", 37.5, 31.7, -10.9, 93.2, 18.3, 57.7),
    ("피에스케이홀딩스", 35.7, 28.6, -15.9, 95.9, 22.4, 53.3),
    ("솔브레인", 31.1, 26.0, -13.9, 82.7, 21.9, 49.2),
    ("이수페타시스", 24.5, 16.3, -29.7, 89.0, 34.8, 38.3),
    ("심텍", 18.0, 6.8, -47.4, 97.3, 44.8, 33.2),
    ("테스", 13.0, 5.9, -35.2, 70.1, 44.0, 24.0),
    ("HPSP", 11.8, 5.7, -31.6, 62.6, 43.4, 21.7),
    ("티씨케이", 9.5, 4.7, -28.9, 54.0, 43.9, 18.1),
    ("ISC", -18.0, -23.3, -52.2, 22.8, 76.4, 4.5),
]


def simulate(
    n: int = 250_000,
    seed: int = 20270923,
    rho: float = 0.65,
    width: float = 1.0,
    eps_scale: float = 1.0,
    per_mode: str = "author",
    per_mult: np.ndarray | float | None = None,
    cb_simtek: bool = False,
):
    rng = np.random.default_rng(seed)
    names = [r[0] for r in ROWS]
    gindex = {"mat": 0, "sub": 1, "eq": 2, "sock": 3}
    g = np.array([gindex[r[1]] for r in ROWS])
    price = np.array([r[2] for r in ROWS], float)
    sales0 = np.array([r[3] for r in ROWS], float) * eps_scale
    op0 = np.array([r[4] for r in ROWS], float) * eps_scale
    ni0 = np.array([r[5] for r in ROWS], float) * eps_scale
    eps0 = np.array([r[6] for r in ROWS], float) * eps_scale
    sig_s = np.array([r[7] for r in ROWS], float) * width
    sig_m = np.array([r[8] for r in ROWS], float) * width
    k = np.array([r[9] for r in ROWS], float)
    sig_r = np.array([r[10] for r in ROWS], float) * width
    if per_mode == "author":
        per0 = np.array([r[11] for r in ROWS], float)
    elif per_mode == "12mf":
        per0 = np.array([r[12] for r in ROWS], float)
    elif per_mode == "20":
        per0 = np.full(len(ROWS), 20.0)
    else:
        raise ValueError(per_mode)
    if per_mult is not None:
        per0 = per0 * np.asarray(per_mult, float)
    sig_p = np.full(len(ROWS), 0.18) * width
    psk = np.array([r[13] for r in ROWS])

    mkt = rng.standard_normal(n)
    sec = rng.standard_normal((n, 4))
    id_s = rng.standard_normal((n, 9))
    id_m = rng.standard_normal((n, 9))
    id_p = rng.standard_normal((n, 9))
    id_r = rng.standard_normal((n, 9))
    z_s = np.sqrt(0.35) * mkt[:, None] + np.sqrt(0.25) * sec[:, g] + np.sqrt(0.40) * id_s
    z_m = 0.50 * z_s + np.sqrt(0.75) * id_m
    # Written link: corr(sales latent, PER latent) = 0.60 * rho = 0.39 at the base rho.
    rho_sp = 0.60 * rho
    z_p = rho_sp * z_s + np.sqrt(max(0.0, 1.0 - rho_sp**2)) * id_p

    sales = sales0 * np.exp(sig_s * z_s - 0.5 * sig_s**2)
    c = 0.50 * sig_s * sig_m
    margin = (op0 / sales0) - c + sig_m * z_m
    op = sales * margin
    r0 = ni0 - k * op0
    resid = r0 + np.abs(r0) * sig_r * id_r
    for i, flag in enumerate(psk):
        if flag:
            resid[:, i] = r0[i] * np.exp(sig_r[i] * id_r[:, i] - 0.5 * sig_r[i] ** 2)
    ni = k * op + resid
    eps = eps0 * (ni / ni0)
    if cb_simtek:
        eps[:, names.index("심텍")] = eps[:, names.index("심텍")] / 1.03375
    per = per0 * np.exp(sig_p * z_p - 0.5 * sig_p**2)
    px = np.where(eps > 0.0, eps * per, 0.0)
    ret = px / price - 1.0
    return names, price, ret, eps


def stats(names, price, ret, eps):
    rank = np.argsort(-ret, axis=1)
    top3 = np.zeros(len(names))
    for i in range(3):
        np.add.at(top3, rank[:, i], 1)
    top3 /= len(ret)
    out = {}
    for i, name in enumerate(names):
        r = ret[:, i]
        out[name] = dict(
            mean=float(r.mean() * 100),
            med=float(np.median(r) * 100),
            p10=float(np.quantile(r, 0.10) * 100),
            p90=float(np.quantile(r, 0.90) * 100),
            loss=float((r < 0).mean() * 100),
            top3=float(top3[i] * 100),
            px=float(price[i] * (1.0 + r).mean()),
            neg=int((eps[:, i] <= 0).sum()),
        )
    return out


def top3_means(names, ret):
    order = np.argsort(-ret.mean(axis=0))
    return [(names[i], float(ret[:, i].mean() * 100)) for i in order[:3]]


def grid_counts(names, ret):
    gindex = {"mat": 0, "sub": 1, "eq": 2, "sock": 3}
    g = np.array([gindex[r[1]] for r in ROWS])
    counts = {name: 0 for name in names}
    for combo in product((0.85, 1.0, 1.15), repeat=4):
        mult = np.array([combo[gi] for gi in g])
        means = ((1.0 + ret) * mult - 1.0).mean(axis=0)
        for i in np.argsort(-means)[:3]:
            counts[names[i]] += 1
    return counts


def main():
    names, price, ret, eps = simulate(n=250_000)
    base = stats(names, price, ret, eps)
    ih, ip = names.index("한솔케미칼"), names.index("피에스케이홀딩스")
    p_win = float((ret[:, ih] > ret[:, ip]).mean() * 100)
    counts = grid_counts(names, ret)

    print("BASE 250,000  seed=20270923  corr(sales, PER)=0.39")
    print(f"{'rank':<4} {'name':<18} {'mean':>8} {'pub':>7} {'med':>7} {'p10':>7} {'p90':>7} {'loss':>6} {'top3':>6}")
    order = sorted(base, key=lambda k: -base[k]["mean"])
    for i, name in enumerate(order, 1):
        s = base[name]
        pub = next(row for row in PUBLISHED if row[0] == name)
        print(
            f"{i:<4} {name:<18} {s['mean']:7.2f}% {pub[1]:6.1f}% {s['med']:6.2f}% "
            f"{s['p10']:6.1f}% {s['p90']:6.1f}% {s['loss']:5.1f}% {s['top3']:5.1f}%"
        )
    print(f"P(한솔 > 홀딩스) = {p_win:.2f}%   published 52.6%")
    print(f"심텍 non-positive EPS paths = {base['심텍']['neg']} / 250000   published 41")
    print("81-grid top3 counts:", " ".join(f"{k}:{counts[k]}" for k in order))

    print("\nSENSITIVITY top3 by mean upside (100,000 paths)")
    specs = [
        ("12MF PER on 2027 EPS", dict(per_mode="12mf")),
        ("all 20x", dict(per_mode="20")),
        ("rho 0", dict(rho=0.0)),
        ("width 1.5x", dict(width=1.5)),
        ("EPS -20%", dict(eps_scale=0.8)),
        ("EPS and PER -20%", dict(eps_scale=0.8, per_mult=0.8)),
        ("Simtek residual CB", dict(cb_simtek=True)),
    ]
    for label, kw in specs:
        nms, _, r, e = simulate(n=100_000, **kw)
        tops = top3_means(nms, r)
        extra = ""
        if kw.get("cb_simtek"):
            extra = f"   심텍 {float(r[:, nms.index('심텍')].mean()*100):.2f}%"
        print(label, " / ".join(f"{a} {b:.1f}%" for a, b in tops), extra, f"neg {int((e<=0).sum())}")


if __name__ == "__main__":
    main()
