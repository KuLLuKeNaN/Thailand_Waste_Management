from dataclasses import dataclass


@dataclass
class SavingsOutput:
    estimated_waste_reduction_pct: float
    estimated_savings_thb: float
    estimated_avoided_waste_kg: float
    notes: list[str]


def estimate_savings(
    recommended_portions: int,
    baseline_portions: int,
    cost_thb_per_portion: float,
    typical_overproduction_pct: float = 0.10,
    target_reduction_range: tuple[float, float] = (0.08, 0.15),
    grams_per_portion_waste_equivalent: float = 180.0,
) -> SavingsOutput:
    notes: list[str] = []

    baseline = max(1, int(baseline_portions))
    rec = max(1, int(recommended_portions))
    cost = max(0.0, float(cost_thb_per_portion))

    if rec >= baseline:
        reduction_pct = target_reduction_range[0] * 0.6
        notes.append("Recommendation is not lower than baseline; conservative savings applied.")
    else:
        delta = (baseline - rec) / baseline
        reduction_pct = min(
            target_reduction_range[1],
            max(target_reduction_range[0], delta + 0.03),
        )
        notes.append(
            "Recommendation reduces baseline; savings estimated from portion reduction + benchmark uplift."
        )

    wasted_portions_baseline = baseline * typical_overproduction_pct
    avoided_wasted_portions = wasted_portions_baseline * reduction_pct

    estimated_savings = avoided_wasted_portions * cost
    avoided_waste_kg = (avoided_wasted_portions * grams_per_portion_waste_equivalent) / 1000.0

    notes.append(f"Assumed typical overproduction: {typical_overproduction_pct*100:.0f}% of baseline.")
    notes.append(f"Benchmark-aligned avoidable waste reduction: {reduction_pct*100:.1f}%.")

    return SavingsOutput(
        estimated_waste_reduction_pct=reduction_pct,
        estimated_savings_thb=estimated_savings,
        estimated_avoided_waste_kg=avoided_waste_kg,
        notes=notes,
    )
