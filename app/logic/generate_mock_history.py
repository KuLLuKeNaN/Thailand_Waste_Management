import os
import random
from datetime import date, timedelta
import csv

WEATHER = ["Sunny", "Cloudy", "Rainy", "Storm"]
DAY_TYPE = ["Weekday", "Weekend", "Holiday"]
EVENT = ["None", "Medium", "High"]

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def pick_day_type(d: date) -> str:
    if d.weekday() in (5, 6):  # Sat/Sun
        return "Weekend"
    return "Weekday"

def generate_rows(days=60, seed=42):
    rng = random.Random(seed)
    rows = []
    start = date.today() - timedelta(days=days-1)

    for i in range(days):
        d = start + timedelta(days=i)
        day_type = pick_day_type(d)

        # sometimes mark a holiday
        if rng.random() < 0.06:
            day_type = "Holiday"

        weather = rng.choices(WEATHER, weights=[0.45, 0.30, 0.20, 0.05])[0]
        event_level = rng.choices(EVENT, weights=[0.70, 0.22, 0.08])[0]

        # occupancy
        base_occ = rng.uniform(0.45, 0.95)
        if day_type in ("Weekend", "Holiday"):
            base_occ += rng.uniform(0.05, 0.12)
        if event_level == "High":
            base_occ += rng.uniform(0.05, 0.10)
        occupancy_rate = clamp(base_occ, 0.30, 0.98)

        # expected guests (roughly proportional)
        expected_guests = int(round(120 + occupancy_rate * 320 + rng.uniform(-30, 30)))
        expected_guests = max(0, expected_guests)

        # baseline: kitchens tend to overproduce
        # demand factor
        day_factor = 1.0 + (0.08 if day_type == "Weekend" else 0.0) + (0.12 if day_type == "Holiday" else 0.0)
        event_factor = 1.0 + (0.06 if event_level == "Medium" else 0.0) + (0.12 if event_level == "High" else 0.0)
        weather_factor = 1.0 - (0.04 if weather == "Rainy" else 0.0) - (0.08 if weather == "Storm" else 0.0)

        true_need = int(round(expected_guests * 0.85 * day_factor * event_factor * weather_factor))
        true_need = max(10, true_need)

        baseline_portions = int(round(true_need * (1.12 + rng.uniform(-0.03, 0.05))))  # ~12% over
        baseline_portions = max(10, baseline_portions)

        # recommended: closer to true need, with small safety buffer
        recommended_portions = int(round(true_need * (1.03 + rng.uniform(-0.02, 0.03))))
        recommended_portions = max(10, recommended_portions)

        # actual: sometimes follows recommendation, sometimes not
        if rng.random() < 0.72:
            actual_cooked = int(round(recommended_portions * (1 + rng.uniform(-0.02, 0.03))))
        else:
            actual_cooked = int(round(recommended_portions * (1 + rng.uniform(0.04, 0.12))))
        actual_cooked = max(10, actual_cooked)

        rows.append({
            "date": d.isoformat(),
            "expected_guests": expected_guests,
            "occupancy_rate": round(occupancy_rate, 2),
            "weather": weather,
            "day_type": day_type,
            "event_level": event_level,
            "baseline_portions": baseline_portions,
            "recommended_portions": recommended_portions,
            "actual_cooked": actual_cooked,
        })

    return rows

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "app", "data")
    os.makedirs(base_dir, exist_ok=True)
    out_path = os.path.join(base_dir, "training_history.csv")

    rows = generate_rows(days=90, seed=42)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("Wrote:", out_path, "rows:", len(rows))

if __name__ == "__main__":
    main()
