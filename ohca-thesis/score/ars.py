"""Exploratory OHCA-ARS (Age-Rhythm-Sex) integer draft. Not a clinical score."""

from __future__ import annotations

from dataclasses import dataclass

AGE_CUTOFF = 59
POINTS = {"age": 3, "shockable": 2, "male": 1}


@dataclass(frozen=True)
class ArsResult:
    applicable: bool
    reason: str
    age_points: int
    shockable_points: int
    male_points: int
    door_score: int | None

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def ars_door(
    age: float,
    male: bool,
    shockable: bool,
    stemi: bool = False,
) -> ArsResult:
    """Door score 0-6. No CK-MB. No Low/High bands. No probability."""
    if stemi:
        return ArsResult(False, "STEMI: out of scope", 0, 0, 0, None)
    if age < 19:
        return ArsResult(False, "Derivation cohort was adults >=19", 0, 0, 0, None)

    age_pts = POINTS["age"] if age >= AGE_CUTOFF else 0
    shock_pts = POINTS["shockable"] if shockable else 0
    male_pts = POINTS["male"] if male else 0
    return ArsResult(
        applicable=True,
        reason="exploratory OHCA-ARS door integer; not validated",
        age_points=age_pts,
        shockable_points=shock_pts,
        male_points=male_pts,
        door_score=age_pts + shock_pts + male_pts,
    )


if __name__ == "__main__":
    examples = [
        dict(age=66, male=True, shockable=True),
        dict(age=62, male=True, shockable=False),
        dict(age=70, male=False, shockable=True),
        dict(age=45, male=False, shockable=False),
        dict(age=66, male=True, shockable=True, stemi=True),
    ]
    for ex in examples:
        print(ex, "->", ars_door(**ex))
