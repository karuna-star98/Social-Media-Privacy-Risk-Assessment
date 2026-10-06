"""
FILE: backend/services/recommendation_engine.py
PURPOSE: Personalised recommendations, prioritised IMMEDIATE > IMPORTANT > GOOD PRACTICE.
"""
from .questionnaire import QUESTIONS, QUESTION_BY_ID, IMMEDIATE, IMPORTANT, GOOD

PRIORITY_ORDER = {IMMEDIATE: 0, IMPORTANT: 1, GOOD: 2}


def generate_recommendations(findings):
    recs = []
    for f in findings:
        q = QUESTION_BY_ID.get(f["finding_type"])
        if q:
            recs.append({"finding_type": q["id"], "category": q["category"], "risk": q["finding"],
                         "recommendation": q["recommendation"], "priority": q["priority"],
                         "impact": f.get("impact", 0)})
    recs.sort(key=lambda r: (PRIORITY_ORDER[r["priority"]], -r["impact"]))
    return recs


def recommendation_catalog():
    """Rows used to seed the RECOMMENDATIONS table (generic advice - no user data)."""
    return [(q["id"], q["recommendation"], q["priority"]) for q in QUESTIONS]
