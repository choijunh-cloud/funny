"""ACES bedside score for Non-STEMI OHCA culprit probability (derivation only)."""

from __future__ import annotations

from dataclasses import dataclass


AGE_CUTOFF = 59
CKMB_DELTA_CUTOFF = 21.4  # ng/mL
POINTS = {"age": 3, "shockable": 2, "male": 1, "ckmb_delta": 1}


@dataclass(frozen=True)
class AcesResult:
    applicable: bool
    reason: str
    age_points: int
    shockable_points: int
    male_points: int
    ckmb_points: int | None
    door_score: int
    full_score: int | None
    band: str

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def _band(score: int) -> str:
    if score <= 2:
        return "low"
    if score <= 4:
        return "intermediate"
    return "high"


def aces_score(
    age: float,
    male: bool,
    shockable: bool,
    ckmb_first: float | None = None,
    ckmb_second: float | None = None,
    stemi: bool = False,
) -> AcesResult:
    """Integer ACES from published standardized betas (not re-fit on patients)."""
    if stemi:
        return AcesResult(False, "STEMI: do not use ACES; consider immediate CAG", 0, 0, 0, None, 0, None, "na")
    if age < 19:
        return AcesResult(False, "Derivation cohort was adults >=19 years", 0, 0, 0, None, 0, None, "na")

    age_pts = POINTS["age"] if age >= AGE_CUTOFF else 0
    shock_pts = POINTS["shockable"] if shockable else 0
    male_pts = POINTS["male"] if male else 0
    door = age_pts + shock_pts + male_pts

    ck_pts: int | None = None
    full: int | None = None
    if ckmb_first is not None and ckmb_second is not None:
        ck_pts = POINTS["ckmb_delta"] if (ckmb_second - ckmb_first) >= CKMB_DELTA_CUTOFF else 0
        full = door + ck_pts

    used = full if full is not None else door
    return AcesResult(
        applicable=True,
        reason="Non-STEMI ACES",
        age_points=age_pts,
        shockable_points=shock_pts,
        male_points=male_pts,
        ckmb_points=ck_pts,
        door_score=door,
        full_score=full,
        band=_band(used),
    )


if __name__ == "__main__":
    examples = [
        dict(age=66, male=True, shockable=True, ckmb_first=5.6, ckmb_second=70.0),
        dict(age=62, male=True, shockable=False),
        dict(age=70, male=False, shockable=True),
        dict(age=45, male=False, shockable=False, ckmb_first=2.9, ckmb_second=3.3),
        dict(age=66, male=True, shockable=True, stemi=True),
    ]
    for ex in examples:
        print(ex, "->", aces_score(**ex))
