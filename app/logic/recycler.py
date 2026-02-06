from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RecyclerPartner:
    id: str
    name: str
    accepts: List[str]
    eta_window: str
    notes: str

def get_demo_partners() -> List[RecyclerPartner]:
    return [
        RecyclerPartner(
            id="R1",
            name="Bangkok Compost Co-op",
            accepts=["Compost"],
            eta_window="18:00–20:00",
            notes="Accepts veg/fruit scraps, bread, rice. No plastics.",
        ),
        RecyclerPartner(
            id="R2",
            name="City Biogas Facility",
            accepts=["Biogas"],
            eta_window="16:00–19:00",
            notes="Accepts meat/fish leftovers. Sealed bags required.",
        ),
        RecyclerPartner(
            id="R3",
            name="GreenCycle Recyclers",
            accepts=["Recycle"],
            eta_window="10:00–12:00",
            notes="Accepts clean bottles/packaging. No organic waste.",
        ),
    ]

def choose_partner(waste_stream: str) -> RecyclerPartner:
    partners = get_demo_partners()
    for p in partners:
        if waste_stream in p.accepts:
            return p
    return partners[0]
