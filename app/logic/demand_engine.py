from dataclasses import dataclass
import math


@dataclass
class DemandInputs:
    target_meal: str
    expected_guests: int
    occupancy_rate: float
    weather: str
    day_type: str
    event_level: str


@dataclass
class DemandOutput:
    recommended_portions: int
    baseline_portions: int
    demand_multiplier: float
    explanation: list[str]


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _weather_factor(weather: str) -> float:
    w = weather.lower()
    if w == "rainy":
        return 0.88
    if w == "storm":
        return 0.82
    if w == "cloudy":
        return 0.96
    return 1.00


def _day_factor(day_type: str) -> float:
    d = day_type.lower()
    if d == "weekend":
        return 1.08
    if d == "holiday":
        return 1.12
    return 1.00


def _event_factor(event_level: str) -> float:
    e = event_level.lower()
    if e == "high":
        return 1.15
    if e == "medium":
        return 1.07
    return 1.00


def _meal_buffer(target_meal: str) -> float:
    m = target_meal.lower()
    if "breakfast" in m:
        return 0.95
    if "lunch" in m:
        return 0.97
    return 0.98


def estimate_portions(inp: DemandInputs) -> DemandOutput:
    explanation: list[str] = []

    expected_guests = max(0, int(inp.expected_guests))
    occupancy = _clamp(float(inp.occupancy_rate), 0.0, 1.0)

    baseline = int(round(expected_guests * (0.85 + 0.30 * occupancy)))
    baseline = max(10, baseline)

    wf = _weather_factor(inp.weather)
    df = _day_factor(inp.day_type)
    ef = _event_factor(inp.event_level)
    buf = _meal_buffer(inp.target_meal)

    multiplier = wf * df * ef * buf
    multiplier = _clamp(multiplier, 0.70, 1.35)

    rec = int(math.ceil(baseline * multiplier))
    rec = max(10, rec)

    explanation.append(f"Baseline based on expected guests & occupancy: {baseline} portions")
    explanation.append(f"Weather factor ({inp.weather}): x{wf:.2f}")
    explanation.append(f"Day factor ({inp.day_type}): x{df:.2f}")
    explanation.append(f"Event factor ({inp.event_level}): x{ef:.2f}")
    explanation.append(f"Risk buffer for {inp.target_meal}: x{buf:.2f}")
    explanation.append(f"Final multiplier: x{multiplier:.2f}")

    return DemandOutput(
        recommended_portions=rec,
        baseline_portions=baseline,
        demand_multiplier=multiplier,
        explanation=explanation,
    )
