"""
FILE: backend/services/assessment_engine.py
PURPOSE: Orchestrates the pipeline: validate -> extract features -> score -> findings -> recommendations.
"""
from .questionnaire import QUESTIONS, SCALES, validate_answers
from .scoring_engine import calculate_privacy_risk
from .findings_engine import generate_privacy_findings
from .recommendation_engine import generate_recommendations


def extract_privacy_features(answers):
    """Convert questionnaire answers into numeric risk features (one per question).
    risk: 0.0 (best) .. 1.0 (worst); weight: importance inside its category."""
    clean = validate_answers(answers)
    return {q["id"]: {"category": q["category"], "answer": clean[q["id"]],
                      "risk": SCALES[q["scale"]][clean[q["id"]]], "weight": q["weight"]}
            for q in QUESTIONS}


def run_assessment(answers, weights=None):
    features = extract_privacy_features(answers)
    result = calculate_privacy_risk(features, weights)
    findings = generate_privacy_findings(features, result)
    recommendations = generate_recommendations(findings["findings"])
    return {**result, **findings, "recommendations": recommendations}
