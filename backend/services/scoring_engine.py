"""
FILE: backend/services/scoring_engine.py
PURPOSE: Category scores (0-100) + configurable-weight overall score + risk classification.
HIGHER SCORE = HIGHER ASSESSED EXPOSURE/RISK.

EDUCATIONAL ASSUMPTION: the weights and thresholds below are teaching assumptions.
They must be validated/calibrated before any professional risk decision.
"""
from collections import defaultdict
from .questionnaire import CATEGORIES

DEFAULT_WEIGHTS = {
    "profile": 0.10, "personal": 0.15, "location": 0.15, "content": 0.10,
    "connections": 0.10, "tagging": 0.05, "account": 0.15, "apps": 0.05,
    "social_eng": 0.10, "footprint": 0.05,
}
# upper bound (inclusive) of each level, on the rounded integer score
THRESHOLDS = [(20, "LOW"), (40, "MODERATE"), (70, "HIGH"), (100, "CRITICAL")]


def validate_weights(weights):
    if set(weights) != set(CATEGORIES):
        raise ValueError("weights must define exactly the 10 categories")
    if any(w < 0 for w in weights.values()):
        raise ValueError("weights must not be negative")
    if abs(sum(weights.values()) - 1.0) > 0.001:
        raise ValueError("weights must sum to 1.0")
    return weights


def classify_risk(score):
    """0-20 LOW, 21-40 MODERATE, 41-70 HIGH, 71-100 CRITICAL."""
    score = int(round(score))
    for upper, level in THRESHOLDS:
        if score <= upper:
            return level
    return "CRITICAL"


def _round(x):
    return int(x + 0.5)


def _raw_category_scores(features):
    """Weighted mean of question risks per category, scaled to 0-100 (float)."""
    num, den = defaultdict(float), defaultdict(float)
    for f in features.values():
        num[f["category"]] += f["risk"] * f["weight"]
        den[f["category"]] += f["weight"]
    return {c: (100.0 * num[c] / den[c] if den[c] else 0.0) for c in CATEGORIES}


def calculate_category_scores(features):
    return {c: _round(v) for c, v in _raw_category_scores(features).items()}


def calculate_privacy_risk(features, weights=None):
    """Return {overall_score, risk_level, category_scores, weights}."""
    w = validate_weights(weights or DEFAULT_WEIGHTS)
    raw = _raw_category_scores(features)
    overall = _round(sum(w[c] * raw[c] for c in CATEGORIES))
    return {"overall_score": overall, "risk_level": classify_risk(overall),
            "category_scores": {c: _round(v) for c, v in raw.items()}, "weights": dict(w)}
