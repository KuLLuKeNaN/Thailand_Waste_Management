from dataclasses import dataclass


@dataclass
class GreenStarResult:
    is_active: bool
    score: int
    reason: str


def evaluate_green_star(
    estimated_waste_reduction_pct: float,
    days_used_in_a_row: int,
    min_reduction_pct: float = 0.10,
    min_days: int = 7,
) -> GreenStarResult:
    r = float(estimated_waste_reduction_pct)
    d = int(days_used_in_a_row)

    score = 0
    if r >= min_reduction_pct:
        score += 60
    score += min(40, max(0, d) * 6)

    is_active = (r >= min_reduction_pct) and (d >= min_days)

    if is_active:
        reason = "Green Star is active: consistent measurable waste reduction."
    else:
        reason = "Green Star not active yet: increase reduction and/or maintain consistent usage."

    return GreenStarResult(is_active=is_active, score=score, reason=reason)
