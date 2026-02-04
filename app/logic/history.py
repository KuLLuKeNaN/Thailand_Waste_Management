from datetime import date, timedelta
import random

def generate_fake_history(
    today_baseline: int,
    today_recommended: int,
    today_avoided_kg: float,
    days: int = 7,
    seed: int = 42,
):
    random.seed(seed)
    rows = []

    for i in range(days):
        d = date.today() - timedelta(days=(days - 1 - i))

        baseline = max(10, int(today_baseline * (1 + random.uniform(-0.08, 0.08))))
        recommended = max(10, int(today_recommended * (1 + random.uniform(-0.06, 0.06))))

        avoided_kg = max(
            0.0,
            today_avoided_kg * (1 + random.uniform(-0.15, 0.15))
        )

        rows.append({
            "date": d.isoformat(),
            "baseline": baseline,
            "recommended": recommended,
            "avoided_kg": round(avoided_kg, 2),
        })

    return rows
