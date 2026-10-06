"""
FILE: backend/services/analytics.py
PURPOSE: Aggregate dashboard statistics over the SYNTHETIC dataset (fictional records only).
"""
import csv, os
from collections import Counter
from .questionnaire import QUESTIONS, QUESTION_BY_ID, SCALES, CATEGORIES
from .scoring_engine import classify_risk
from .improvement_simulator import simulate_improvement

TOP_FIXES = ["phone_private", "disable_realtime", "enable_mfa", "enable_tag_review",
             "verify_requests", "review_apps", "unique_passwords"]
ACCOUNT_CONTROLS = {"G1": "MFA enabled", "G2": "Unique passwords", "G3": "Password manager",
                    "G4": "Login alerts", "G5": "Recovery info reviewed", "G6": "Sessions reviewed"}
FOOTPRINT_CONTROLS = {"J1": "Old posts reviewed", "J3": "Old comments reviewed",
                      "J4": "Settings reviewed", "J5": "Public view checked"}


def _load(path):
    if not os.path.exists(path):                       # fall back to in-memory generation
        from data.generate_dataset import generate_records
        return generate_records(1000, seed=42)
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _pct(rows, qid, protective=True):
    ok = sum(1 for r in rows if SCALES[QUESTION_BY_ID[qid]["scale"]][r[qid]] == 0.0)
    return round(100 * ok / len(rows), 1)


def synthetic_dashboard(path):
    rows = _load(path)
    n = len(rows)
    scores = [int(r["risk_score"]) for r in rows]
    weak = Counter()
    for r in rows:
        for q in QUESTIONS:
            if SCALES[q["scale"]][r[q["id"]]] >= 0.5:
                weak[q["id"]] += 1
    sample = rows[:300]                                # keep the demo fast
    before = after = 0
    for r in sample:
        res = simulate_improvement({q["id"]: r[q["id"]] for q in QUESTIONS}, TOP_FIXES)
        before += res["before"]["overall_score"]
        after += res["after"]["overall_score"]
    return {
        "records": n,
        "avg_score": round(sum(scores) / n, 1),
        "level_distribution": dict(Counter(classify_risk(s) for s in scores)),
        "avg_category_scores": {c: round(sum(int(r["cat_" + c]) for r in rows) / n, 1) for c in CATEGORIES},
        "category_names": {c: v[1] for c, v in CATEGORIES.items()},
        "top_weaknesses": [{"label": QUESTION_BY_ID[q]["finding"], "percent": round(100 * k / n, 1)}
                           for q, k in weak.most_common(8)],
        "account_controls": [{"label": l, "percent": _pct(rows, q)} for q, l in ACCOUNT_CONTROLS.items()],
        "footprint_controls": [{"label": l, "percent": _pct(rows, q)} for q, l in FOOTPRINT_CONTROLS.items()],
        "improvement": {"avg_before": round(before / len(sample), 1), "avg_after": round(after / len(sample), 1),
                        "fixes": TOP_FIXES},
    }
