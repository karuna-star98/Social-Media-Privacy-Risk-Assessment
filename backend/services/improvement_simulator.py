"""
FILE: backend/services/improvement_simulator.py
PURPOSE: "What happens if I improve my settings?" - re-scores answers after applying changes.
LABEL: a framework simulation, NOT a guarantee of real-world safety.
"""
from .questionnaire import QUESTION_BY_ID, ValidationError, validate_answers
from .assessment_engine import extract_privacy_features
from .scoring_engine import calculate_privacy_risk

SIM_DISCLAIMER = ("This is a framework simulation based on educational weights. It is not a "
                  "guarantee that an account will or will not be compromised.")

# preset key -> (label, {question_id: improved answer})
PRESETS = {
    "profile_private":      ("Make profile private", {"A1": "PRIVATE", "A2": "NO"}),
    "phone_private":        ("Make phone number private", {"B1": "NO"}),
    "email_private":        ("Make personal email private", {"B2": "NO"}),
    "birthday_private":     ("Hide full birth date", {"B3": "NO"}),
    "home_info_private":    ("Remove home information", {"B4": "NO"}),
    "location_private":     ("Hide home/work location", {"C4": "NO"}),
    "disable_realtime":     ("Disable real-time location sharing", {"C1": "NO"}),
    "disable_geotagging":   ("Turn off geotagging", {"C2": "NO"}),
    "no_checkins":          ("Stop public check-ins", {"C3": "NO"}),
    "travel_private":       ("Stop posting live travel plans", {"C5": "NO"}),
    "posts_friends_only":   ("Limit posts to friends", {"D1": "FRIENDS"}),
    "verify_requests":      ("Reject/verify unknown requests", {"E1": "NO", "E2": "NO"}),
    "enable_tag_review":    ("Enable tag review", {"F1": "NO", "F2": "YES", "F3": "NO"}),
    "enable_mfa":           ("Enable MFA", {"G1": "YES"}),
    "unique_passwords":     ("Use unique passwords + manager", {"G2": "NO", "G3": "YES"}),
    "enable_login_alerts":  ("Enable login alerts", {"G4": "YES"}),
    "review_apps":          ("Review & remove third-party apps", {"H1": "YES", "H2": "YES", "H3": "YES"}),
    "never_share_codes":    ("Never share verification codes", {"I3": "NO"}),
    "avoid_links":          ("Stop clicking unexpected links", {"I2": "NO"}),
    "review_old_posts":     ("Review old posts", {"J1": "YES", "J3": "YES"}),
    "review_settings":      ("Review privacy settings regularly", {"J4": "YES", "J5": "YES"}),
}


def list_presets():
    return [{"key": k, "label": v[0]} for k, v in PRESETS.items()]


def _resolve_changes(changes):
    """Accept a list of preset keys and/or a {question_id: answer} dict."""
    merged = {}
    if isinstance(changes, dict):
        changes = [changes]
    if not isinstance(changes, list) or not changes:
        raise ValidationError(["'changes' must be a non-empty list of preset keys or overrides"])
    for ch in changes:
        if isinstance(ch, str) and ch in PRESETS:
            merged.update(PRESETS[ch][1])
        elif isinstance(ch, dict):
            for qid, ans in ch.items():
                if qid not in QUESTION_BY_ID:
                    raise ValidationError(["Unknown question id in changes"])
                merged[qid] = ans
        else:
            raise ValidationError(["Unknown improvement option"])
    return merged


def simulate_improvement(answers, changes, weights=None):
    before_answers = validate_answers(answers)
    after_answers = validate_answers({**before_answers, **_resolve_changes(changes)})
    before = calculate_privacy_risk(extract_privacy_features(before_answers), weights)
    after = calculate_privacy_risk(extract_privacy_features(after_answers), weights)
    return {
        "before": {k: before[k] for k in ("overall_score", "risk_level", "category_scores")},
        "after": {k: after[k] for k in ("overall_score", "risk_level", "category_scores")},
        "risk_reduction": before["overall_score"] - after["overall_score"],
        "changed_questions": sorted(k for k in after_answers if after_answers[k] != before_answers[k]),
        "disclaimer": SIM_DISCLAIMER,
    }
