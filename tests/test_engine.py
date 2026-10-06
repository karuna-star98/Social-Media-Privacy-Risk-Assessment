"""Engine tests T01-T27 (scoring, findings, recommendations, simulator)."""
import pytest
from backend.services.questionnaire import QUESTIONS, CATEGORIES, QUESTION_BY_ID, extreme_answers
from backend.services.assessment_engine import extract_privacy_features, run_assessment
from backend.services.scoring_engine import (calculate_privacy_risk, classify_risk,
                                             DEFAULT_WEIGHTS, validate_weights)
from backend.services.improvement_simulator import simulate_improvement
from backend.services.content import demo_profile_answers


def test_questionnaire_has_40_plus_questions_and_10_categories():
    assert len(QUESTIONS) >= 40 and len(CATEGORIES) == 10
    assert abs(sum(DEFAULT_WEIGHTS.values()) - 1.0) < 1e-9


def test_T01_fully_private_profile(best):
    r = run_assessment(best)
    assert r["overall_score"] == 0 and r["risk_level"] == "LOW" and r["findings"] == []


def test_T02_fully_public_profile(worst):
    r = run_assessment(worst)
    assert r["overall_score"] == 100 and r["risk_level"] == "CRITICAL"


# T03-T20: one risky setting on an otherwise perfect profile must raise exactly that finding
SINGLE = [("T03 public phone", "B1", "YES", "personal"), ("T04 public email", "B2", "YES", "personal"),
          ("T05 public birthday", "B3", "YES", "personal"), ("T06 public location", "C4", "YES", "location"),
          ("T07 real-time check-ins", "C1", "YES", "location"), ("T08 travel plans", "C5", "YES", "location"),
          ("T09 workplace exposure", "B5", "YES", "personal"), ("T10 education exposure", "B6", "YES", "personal"),
          ("T11 public posts", "D1", "PUBLIC", "content"), ("T12 unknown connections", "E1", "YES", "connections"),
          ("T13 tag review disabled", "F2", "NO", "tagging"), ("T14 MFA disabled", "G1", "NO", "account"),
          ("T15 login alerts disabled", "G4", "NO", "account"), ("T16 password reuse", "G2", "YES", "account"),
          ("T17 apps not reviewed", "H1", "NO", "apps"), ("T18 suspicious links clicked", "I2", "YES", "social_eng"),
          ("T19 old posts not reviewed", "J1", "NO", "footprint"), ("T20 settings not reviewed", "J4", "NO", "footprint")]


@pytest.mark.parametrize("name,qid,ans,cat", SINGLE, ids=[s[0] for s in SINGLE])
def test_single_risk_setting(best, name, qid, ans, cat):
    best[qid] = ans
    r = run_assessment(best)
    assert [f["finding_type"] for f in r["findings"]] == [qid]
    assert r["category_scores"][cat] > 0 and r["overall_score"] > 0
    assert all(s == 0 for c, s in r["category_scores"].items() if c != cat)


def test_T21_category_score_calculation(best):
    for q in QUESTIONS:
        if q["category"] == "personal":
            best[q["id"]] = extreme_answers("worst")[q["id"]]
    scores = calculate_privacy_risk(extract_privacy_features(best))["category_scores"]
    assert scores["personal"] == 100 and sum(v for k, v in scores.items() if k != "personal") == 0


def test_T22_overall_score_uses_weights(best):
    worst = extreme_answers("worst")
    for q in QUESTIONS:
        if q["category"] == "personal":
            best[q["id"]] = worst[q["id"]]
    assert calculate_privacy_risk(extract_privacy_features(best))["overall_score"] == 15      # 15% weight
    custom = dict(DEFAULT_WEIGHTS, personal=0.25, profile=0.0)
    assert calculate_privacy_risk(extract_privacy_features(best), custom)["overall_score"] == 25


@pytest.mark.parametrize("score,level", [(0, "LOW"), (20, "LOW"), (21, "MODERATE"), (40, "MODERATE"),
                                         (41, "HIGH"), (70, "HIGH"), (71, "CRITICAL"), (100, "CRITICAL")])
def test_T23_T25_score_boundaries(score, level):
    assert classify_risk(score) == level


def test_bad_weights_rejected():
    with pytest.raises(ValueError):
        validate_weights(dict(DEFAULT_WEIGHTS, personal=0.9))


def test_T26_recommendations_prioritised_and_personalised(best):
    best.update({"G1": "NO", "B1": "YES", "J5": "NO"})
    recs = run_assessment(best)["recommendations"]
    assert [r["priority"] for r in recs] == ["IMMEDIATE", "IMMEDIATE", "GOOD PRACTICE"]
    assert "multi-factor" in recs[0]["recommendation"].lower() or "phone" in recs[0]["recommendation"].lower()


def test_not_sure_is_flagged(best):
    best["G1"] = "NOT_SURE"
    f = run_assessment(best)["findings"][0]
    assert "not sure" in f["description"]


def test_T27_improvement_simulation_demo_profile():
    demo = demo_profile_answers()
    before = run_assessment(demo)
    res = simulate_improvement(demo, ["phone_private", "birthday_private", "location_private",
                                      "disable_realtime", "travel_private", "verify_requests",
                                      "enable_tag_review", "enable_mfa", "enable_login_alerts", "review_apps"])
    assert res["before"]["overall_score"] == before["overall_score"]
    assert res["risk_reduction"] > 15 and res["after"]["overall_score"] < res["before"]["overall_score"]
    assert "not a guarantee" in res["disclaimer"]


def test_simulation_rejects_unknown_option(best):
    from backend.services.questionnaire import ValidationError
    with pytest.raises(ValidationError):
        simulate_improvement(best, ["nonsense"])
