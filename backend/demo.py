"""
FILE: backend/demo.py
PURPOSE: Command-line run of the FICTIONAL demo profile + improvement simulation (Section 32).
Run:  python -m backend.demo
"""
from .services.questionnaire import CATEGORIES
from .services.assessment_engine import run_assessment
from .services.content import demo_profile_answers, DISCLAIMER
from .services.improvement_simulator import simulate_improvement

FIXES = ["phone_private", "birthday_private", "location_private", "disable_realtime", "no_checkins",
         "travel_private", "verify_requests", "enable_tag_review", "enable_mfa",
         "enable_login_alerts", "review_apps", "review_old_posts"]

if __name__ == "__main__":
    answers = demo_profile_answers()
    r = run_assessment(answers)
    print(f"\nDEMO PROFILE (fictional)\nOVERALL PRIVACY RISK: {r['overall_score']}/100  LEVEL: {r['risk_level']}\n\nCATEGORY SCORES")
    for c, s in r["category_scores"].items():
        print(f"  {CATEGORIES[c][1]:<36}{s:>4}/100")
    print("\nTOP RISKS")
    for i, t in enumerate(r["top_risks"], 1):
        print(f"  {i}. {t}")
    print("\nRECOMMENDATIONS (first 6)")
    for x in r["recommendations"][:6]:
        print(f"  [{x['priority']}] {x['recommendation']}")
    s = simulate_improvement(answers, FIXES)
    print(f"\nSIMULATION: {s['before']['overall_score']} ({s['before']['risk_level']}) -> "
          f"{s['after']['overall_score']} ({s['after']['risk_level']})  | risk reduction: {s['risk_reduction']} points")
    print("\n" + DISCLAIMER)
