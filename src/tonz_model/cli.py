"""전체 분석 실행 → outputs/ 에 리포트 생성.

    python -m tonz_model.cli --paths 30000 --out outputs
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from . import career, report
from .params import ModelParams
from .scenarios import run_scenarios, tornado
from .simulate import simulate, summarize
from .units import fmt_eok, fmt_man


def _json_safe(obj):
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="톤즈 부평점 딜 정량 모델")
    ap.add_argument("--paths", type=int, default=30_000)
    ap.add_argument("--scenario-paths", type=int, default=8_000)
    ap.add_argument("--tornado-paths", type=int, default=6_000)
    ap.add_argument("--out", type=Path, default=Path("outputs"))
    ap.add_argument("--skip-tornado", action="store_true")
    args = ap.parse_args(argv)

    t0 = time.time()
    p = ModelParams()
    args.out.mkdir(parents=True, exist_ok=True)

    print("[1/5] 결정론 엔진…")
    sec_assum = report.assumptions_section(p)
    sec_cap = report.capacity_section(p)
    sec_bep = report.bep_section(p)
    sec_take = report.takehome_section(p)

    print(f"[2/5] 몬테카를로 {args.paths:,}경로…")
    res = simulate(p, n_paths=args.paths)
    s = summarize(res)
    sec_mc = report.mc_section(s, p)

    print("[3/5] 시나리오…")
    scen = run_scenarios(p, n_paths=args.scenario_paths)
    sec_scen = report.scenario_section(scen)

    if args.skip_tornado:
        tor, sec_tor = [], ""
    else:
        print("[4/5] 토네이도…")
        tor = tornado(p, n_paths=args.tornado_paths)
        sec_tor = report.tornado_section(tor)

    print("[5/5] 커리어 비교…")
    cmp_ = career.compare(res)
    sec_career = report.career_section(cmp_, p)

    header = (
        "# 톤즈 부평점 인수 딜 — 정량 모델 결과\n\n"
        f"- 경로 수: {args.paths:,} × 120개월, 시드 {p.sim.seed}\n"
        "- 단위: 만원(내부) / 표기는 억·만원\n"
        "- 재현: `python -m tonz_model.cli`\n\n"
        "> 이 모델의 입력 중 계약서에서 확인되지 않은 항목(이자 유무, 연대보증, "
        "미완제 잔액 처리, '매출 90%'의 정의)은 분포/시나리오로 처리했다. "
        "그 네 줄이 확정되면 분산이 크게 줄어든다.\n\n"
    )

    full = "\n\n".join(
        [header, sec_assum, sec_cap, sec_bep, sec_take, sec_mc, sec_scen, sec_tor, sec_career]
    )
    (args.out / "report.md").write_text(full, encoding="utf-8")

    summary_md = build_summary(p, s, scen, cmp_, tor)
    (args.out / "summary.md").write_text(summary_md, encoding="utf-8")

    payload = {
        "params": p.to_dict(),
        "montecarlo": s,
        "scenarios": scen,
        "tornado": tor,
        "career": cmp_,
    }
    (args.out / "results.json").write_text(
        json.dumps(_json_safe(payload), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"완료 ({time.time() - t0:.1f}s) → {args.out}/report.md, summary.md, results.json")
    return 0


def build_summary(p, s, scen, cmp_, tor) -> str:
    from . import deterministic as det

    bep = det.operating_bep(p)
    r7 = det.required_revenue(p, 7)
    r6 = det.required_revenue(p, 6)
    lines = [
        "# 한 장 요약\n",
        "## 숫자 세 개\n",
        f"1. **운영 손익분기 {fmt_eok(bep)}/월** — 이 밑에서는 부부 월급은 나오지만 원금은 1원도 안 줄어든다.",
        f"2. **7년 완제선 {fmt_eok(r7)}/월, 6년 완제선 {fmt_eok(r6)}/월** (무이자 가정).",
        f"3. **7년 내 소유권 확보 확률 {s['P(7년내 완제)'] * 100:.0f}%, 10년 내 {s['P(10년내 완제)'] * 100:.0f}%**.\n",
        "## 부부가 실제로 손에 쥐는 돈\n",
        f"- 1~5년 부부 합산 세후 월수령 중앙값 **{fmt_man(s['부부세후월_1~5년_중앙'])}** "
        f"(p10 {fmt_man(s['부부세후월_1~5년_p10'])} / p90 {fmt_man(s['부부세후월_1~5년_p90'])})",
        f"- 1인 환산 중앙값 **{fmt_man(cmp_['딜_1인_월세후_중앙'])}**, 시간당 {cmp_['딜_1인_시간당_중앙']:.1f}만원",
        f"- 응급의학 잔류(D-N-Off×4)는 시간당 {cmp_['EM_1인_시간당']:.1f}만원 → 딜은 그 "
        f"**{cmp_['시간당_배율_중앙(딜/EM)']:.2f}배**\n",
        "## 결정적 조항 (계약서에서 확인되면 분산이 접힌다)\n",
    ]
    keys = ["interest_6pct", "profit_split", "deficit_to_balance", "worst_contract", "best_contract"]
    for k in keys:
        if k in scen:
            v = scen[k]
            lines.append(
                f"- **{v['설명']}** → 7년 완제 {v['P(7년내 완제)'] * 100:.0f}%, "
                f"10년 완제 {v['P(10년내 완제)'] * 100:.0f}%, "
                f"부부 세후월 {fmt_man(v['부부세후월_1~5년_중앙'])}"
            )
    if tor:
        lines.append("\n## 결과를 가장 크게 흔드는 변수 5\n")
        for r in tor[:5]:
            lines.append(
                f"- {r['파라미터']} ({r['low']} → {r['high']}): 7년 완제확률 "
                f"{r['metric_low'] * 100:.0f}% → {r['metric_high'] * 100:.0f}% (스윙 {r['swing'] * 100:.0f}%p)"
            )
    lines += [
        "\n## 판정\n",
        f"- P(딜 10년 PV > 부부 둘 다 EM급으로 일했을 때) = **{cmp_['P(딜PV > EM 2인PV)'] * 100:.0f}%**",
        f"- P(딜 10년 PV < 0, 투입 10억도 못 건짐) = **{cmp_['P(딜PV < 0)'] * 100:.0f}%**",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
