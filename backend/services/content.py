"""
FILE: backend/services/content.py
PURPOSE: Static educational content - disclaimer, printable checklist, fictional demo profile.
"""
from .questionnaire import QUESTIONS, SCALES

DISCLAIMER = ("This is an educational privacy-risk framework based on self-reported answers and "
              "assumed weights. It is not a guarantee that an account will or will not be "
              "compromised, and it must be validated before any professional risk decision.")

CHECKLIST = [
    "Review profile visibility", "Hide unnecessary contact information",
    "Review birth-date visibility", "Review location sharing",
    "Avoid unnecessary real-time location posts", "Review tagging permissions",
    "Review followers/friends", "Verify unfamiliar requests", "Enable MFA",
    "Enable login alerts where available", "Review active sessions", "Review connected apps",
    "Remove unused integrations", "Review old public posts", "Review photo privacy",
    "Be cautious with unexpected links", "Never share verification codes",
    "Review privacy settings periodically",
]


def demo_profile_answers():
    """FICTIONAL risky profile ("Demo User") from the project brief. Unspecified items are neutral."""
    neutral = {"VIS": "FRIENDS", "PUB": "NO", "BAD": "SOMETIMES", "GOOD": "SOMETIMES"}
    a = {q["id"]: neutral[q["scale"]] for q in QUESTIONS}
    a.update({"A1": "PUBLIC", "B1": "YES", "B2": "NO", "B3": "YES", "C4": "YES", "C1": "YES",
              "C3": "YES", "C5": "YES", "E1": "YES", "F2": "NO", "G1": "NO", "G4": "NO",
              "H1": "NO", "J1": "NO"})
    return a
