"""Deterministic classroom scoring rules. All matches use word boundaries."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Result:
    category: str
    priority: str
    score: float
    decision: str
    explanation: str


RULES = (
    ("Boundary wall", "P0", 80, ("boundary wall", "compound wall"), ("construction", "gate", "precast"), 3.5),
    ("Civil repair", "P1", 72, ("civil repair", "road repair", "structural repair"), ("concrete", "resurfacing"), 4),
    ("Building construction", "P2", 65, ("classroom", "building construction", "construction of building"), ("construction", "school", "modular"), 4),
)


def classify(text: str) -> Result:
    words = re.sub(r"[^a-z0-9]+", " ", text.lower())
    words = re.sub(r"\bclass\s*rooms?\b", "classroom", words)
    words = re.sub(r"\bwalls\b", "wall", words)
    padded = f" {words} "
    if " catering " in padded:
        return Result("Outside scope", "—", 20, "NO-GO", "Catering activates the exclusion rule before category matching.")
    for category, priority, base, phrases, bonuses, weight in RULES:
        match = next((p for p in phrases if f" {p} " in padded), None)
        if match:
            hits = [term for term in bonuses if f" {term} " in padded]
            score = min(100, base + weight * len(hits))
            detail = f"Matched “{match}”. Base {base} points."
            if hits:
                detail += f" Added {weight * len(hits):g} for {', '.join(hits)}."
            return Result(category, priority, score, "GO" if score >= 60 else "NO-GO", detail)
    return Result("Unclassified", "—", 30, "NO-GO", "No supported construction category matched.")
