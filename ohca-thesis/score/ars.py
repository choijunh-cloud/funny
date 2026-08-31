"""Leftover 3-2-1 arithmetic from a 4-variable beta. Not a locked score."""

from __future__ import annotations

from dataclasses import dataclass

# Youden 59 y is sensitivity analysis only. Weights are NOT locked:
# they were scaled from four-variable betas that still included CK-MB.
AGE_SPLIT_SENSITIVITY = 59
LEFTOVER_POINTS = {"age": 3, "shockable": 2, "male": 1}


@dataclass(frozen=True)
class LeftoverArithmetic:
    applicable: bool
    reason: str
    age_points: int
    shockable_points: int
    male_points: int
    leftover_sum: int | None


def leftover_321(
    age: float,
    male: bool,
    shockable: bool,
    stemi: bool = False,
) -> LeftoverArithmetic:
    """Illustrative leftover points. Re-fit age+rhythm+sex before any integer map."""
    if stemi:
        return LeftoverArithmetic(False, "STEMI: out of scope", 0, 0, 0, None)
    if age < 19:
        return LeftoverArithmetic(False, "Derivation cohort was adults >=19", 0, 0, 0, None)

    age_pts = LEFTOVER_POINTS["age"] if age >= AGE_SPLIT_SENSITIVITY else 0
    shock_pts = LEFTOVER_POINTS["shockable"] if shockable else 0
    male_pts = LEFTOVER_POINTS["male"] if male else 0
    return LeftoverArithmetic(
        applicable=True,
        reason="leftover 3-2-1 from 4-variable beta; not locked; not a score",
        age_points=age_pts,
        shockable_points=shock_pts,
        male_points=male_pts,
        leftover_sum=age_pts + shock_pts + male_pts,
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
        print(ex, "->", leftover_321(**ex))
