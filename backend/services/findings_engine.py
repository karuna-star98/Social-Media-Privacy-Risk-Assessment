"""
FILE: backend/services/findings_engine.py
PURPOSE: Turn risky features into human-readable findings (top risks, severity, high-risk categories).
"""
from .questionnaire import QUESTION_BY_ID, CATEGORIES, IMMEDIATE, IMPORTANT

SEVERITY = {IMMEDIATE: "HIGH", IMPORTANT: "MEDIUM"}   # anything else -> LOW
HIGH_RISK_CATEGORY = 60                               # category score treated as "high risk"


def generate_privacy_findings(features, result):
    items = []
    for qid, f in features.items():
        if f["risk"] < 0.5:
            continue
        q = QUESTION_BY_ID[qid]
        desc = q["finding"] + (" (answered 'not sure' - please check)" if f["answer"] == "NOT_SURE" else "")
        items.append({"finding_type": qid, "category": f["category"],
                      "severity": SEVERITY.get(q["priority"], "LOW"),
                      "description": desc, "impact": round(f["risk"] * f["weight"], 2)})
    items.sort(key=lambda x: -x["impact"])
    return {
        "findings": items,
        "top_risks": [i["description"] for i in items[:5]],
        "high_risk_categories": [CATEGORIES[c][1] for c, s in result["category_scores"].items()
                                 if s >= HIGH_RISK_CATEGORY],
    }
