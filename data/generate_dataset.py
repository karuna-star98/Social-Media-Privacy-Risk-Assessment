"""
FILE: data/generate_dataset.py
PURPOSE: Generate 1,000 FICTIONAL privacy-assessment records (no real people).
Run from project root:  python data/generate_dataset.py
Each record = answers to all 51 questions drawn from a hidden "privacy awareness" level, then
scored by the SAME engine as the app. Output: data/social_media_privacy_assessments.csv
"""
import csv, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backend.services.questionnaire import QUESTIONS, SCALES, CATEGORIES            # noqa: E402
from backend.services.assessment_engine import extract_privacy_features             # noqa: E402
from backend.services.scoring_engine import calculate_privacy_risk                  # noqa: E402

# Readable column name -> question id that feeds it
NAMED = {"profile_visibility": "A1", "phone_public": "B1", "email_public": "B2", "birthday_public": "B3",
         "location_public": "C4", "workplace_public": "B5", "education_public": "B6",
         "relationship_public": "B7", "posts_public": "D1", "location_tagging": "C2",
         "travel_posts": "C5", "unknown_connections": "E1", "tag_review_enabled": "F2",
         "third_party_apps_reviewed": "H1", "mfa_enabled": "G1", "login_alerts_enabled": "G4",
         "password_reuse_reported": "G2", "suspicious_link_awareness": "I2",
         "old_posts_reviewed": "J1", "privacy_settings_reviewed": "J4"}


def _pick(scale, target, rng):
    """Choose an option whose risk is near `target` (0..1), with some randomness."""
    opts = list(SCALES[scale].items())
    weights = [math.exp(-((risk - target) ** 2) / 0.06) for _, risk in opts]
    return rng.choices([o for o, _ in opts], weights)[0]


def generate_records(n=1000, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        base = 1 - rng.betavariate(2, 2)                         # overall tendency to expose (0..1)
        offs = {c: rng.gauss(0, 0.12) for c in CATEGORIES}       # per-category variation
        answers = {q["id"]: _pick(q["scale"], min(1, max(0, rng.gauss(base + offs[q["category"]], 0.2))), rng)
                   for q in QUESTIONS}
        res = calculate_privacy_risk(extract_privacy_features(answers))
        row = {"profile_id": f"SYN-{i:04d}"}
        row.update({col: answers[qid] for col, qid in NAMED.items()})
        row.update({"risk_score": res["overall_score"], "risk_level": res["risk_level"]})
        row.update({"cat_" + c: s for c, s in res["category_scores"].items()})
        row.update(answers)                                      # all 51 answers (A1..J5)
        rows.append(row)
    return rows


def main():
    rows = generate_records()
    out = ROOT / "data" / "social_media_privacy_assessments.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} synthetic records -> {out}")


if __name__ == "__main__":
    main()
