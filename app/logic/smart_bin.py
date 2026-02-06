from dataclasses import dataclass
from typing import Dict, List, Tuple
import random

@dataclass
class SmartBinResult:
    predicted_item: str
    confidence: float
    is_correct_bin: bool
    message: str

ITEM_TO_BIN: Dict[str, str] = {
    "Onion": "Compost",
    "Carrot": "Compost",
    "Rice": "Compost",
    "Bread": "Compost",
    "Chicken": "Biogas",
    "Fish": "Biogas",
    "Plastic Bottle": "Recycle",
}

BINS = ["Compost", "Biogas", "Recycle", "Landfill"]

def classify_demo(selected_item: str, seed: int = 42) -> Tuple[str, float]:
    # Demo: çoğu zaman doğru, bazen karıştırır (jüriye gerçekçilik)
    rng = random.Random(seed + hash(selected_item) % 10000)
    if rng.random() < 0.85:
        return selected_item, round(rng.uniform(0.78, 0.96), 2)
    # yanlış tahmin: başka bir item seç
    other_items = [k for k in ITEM_TO_BIN.keys() if k != selected_item]
    wrong = rng.choice(other_items)
    return wrong, round(rng.uniform(0.45, 0.75), 2)

def evaluate_bin(predicted_item: str, chosen_bin: str) -> SmartBinResult:
    required_bin = ITEM_TO_BIN.get(predicted_item, "Landfill")
    ok = (required_bin == chosen_bin)

    if ok:
        return SmartBinResult(
            predicted_item=predicted_item,
            confidence=1.0,
            is_correct_bin=True,
            message=f"✅ Correct bin. {predicted_item} → {required_bin}",
        )

    return SmartBinResult(
        predicted_item=predicted_item,
        confidence=1.0,
        is_correct_bin=False,
        message=f"🔴 Wrong bin! Detected {predicted_item} → should go to {required_bin} (not {chosen_bin})",
    )
