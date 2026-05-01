from __future__ import annotations
from models.schemas import Issue, ScoreResult

_DEDUCTIONS: dict[str, dict[str, int]] = {
    "P01": {"performance": 20},
    "P02": {"storage": 25},
    "P03": {"performance": 15},
    "P04": {"stability": 5},
    "P05": {"storage": 20},
    "P06": {"stability": 10},
    "P07": {"performance": 10},
    "P08": {"performance": 5},
    "P09": {"performance": 5, "security": 10},
    "P10": {"storage": 10},
}

_WEIGHTS = {"performance": 0.40, "storage": 0.30, "security": 0.15, "stability": 0.15}


def calculate(issues: list[Issue]) -> ScoreResult:
    scores = {"performance": 100, "storage": 100, "security": 100, "stability": 100}

    for issue in issues:
        for dimension, deduction in _DEDUCTIONS.get(issue.code, {}).items():
            scores[dimension] = max(0, scores[dimension] - deduction)

    health = round(sum(scores[d] * w for d, w in _WEIGHTS.items()))

    return ScoreResult(
        health_score=max(0, min(100, health)),
        score_performance=scores["performance"],
        score_storage=scores["storage"],
        score_security=scores["security"],
        score_stability=scores["stability"],
    )
