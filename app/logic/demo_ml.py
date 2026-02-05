import random
from dataclasses import dataclass

import numpy as np


@dataclass
class DemoMLResult:
    ok: bool
    predicted_portions: int
    note: str


def _encode_weather(w: str) -> float:
    m = {"Sunny": 1.00, "Cloudy": 0.98, "Rainy": 0.92, "Storm": 0.86}
    return m.get(w, 1.00)


def _encode_day(day_type: str) -> float:
    m = {"Weekday": 1.00, "Weekend": 1.06, "Holiday": 1.10}
    return m.get(day_type, 1.00)


def _encode_event(e: str) -> float:
    m = {"None": 1.00, "Medium": 1.07, "High": 1.15}
    return m.get(e, 1.00)


def train_and_predict_demo_ml(
    expected_guests: int,
    occupancy_rate: float,
    weather: str,
    day_type: str,
    event_level: str,
    baseline_portions: int,
    seed: int = 42,
) -> DemoMLResult:
    rng = random.Random(seed)

    X = []
    y = []

    for _ in range(120):
        eg = max(0, int(expected_guests * (1 + rng.uniform(-0.20, 0.20))))
        occ = min(1.0, max(0.0, occupancy_rate + rng.uniform(-0.12, 0.12)))

        wf = _encode_weather(weather) * (1 + rng.uniform(-0.04, 0.04))
        df = _encode_day(day_type) * (1 + rng.uniform(-0.03, 0.03))
        ef = _encode_event(event_level) * (1 + rng.uniform(-0.03, 0.03))

        target = int(
            round(
                max(
                    10,
                    baseline_portions
                    * wf
                    * df
                    * ef
                    * (0.92 + 0.16 * occ)
                    * (1 + rng.uniform(-0.03, 0.03)),
                )
            )
        )

        X.append([eg, occ, wf, df, ef])
        y.append(target)

    Xn = np.array(X, dtype=float)
    yn = np.array(y, dtype=float)

    Xb = np.hstack([np.ones((Xn.shape[0], 1)), Xn])

    lam = 1.0
    A = Xb.T @ Xb + lam * np.eye(Xb.shape[1])
    b = Xb.T @ yn
    w = np.linalg.solve(A, b)

    feat = np.array(
        [
            [
                1.0,
                float(expected_guests),
                float(occupancy_rate),
                _encode_weather(weather),
                _encode_day(day_type),
                _encode_event(event_level),
            ]
        ]
    )

    pred = float((feat @ w).ravel()[0])


    pred_int = max(10, int(round(pred)))

    return DemoMLResult(
        ok=True,
        predicted_portions=pred_int,
        note="ML ON (demo-trained on synthetic data)",
    )
