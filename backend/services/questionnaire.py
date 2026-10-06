"""
FILE: backend/services/questionnaire.py
PURPOSE: The privacy questionnaire (51 questions, 10 categories) + input validation.

Privacy-by-design note: every question asks "is X visible / enabled?" and NEVER asks
the user to type the actual phone number, email, address, birth date or password.
Only answers from fixed option lists are accepted (no free text), which also removes
most injection / XSS surface.
"""
from collections import OrderedDict

# --- Answer scales: option -> risk contribution (0.0 = lowest risk, 1.0 = highest) ---
SCALES = {
    "VIS":  {"PUBLIC": 1.0, "FRIENDS": 0.5, "PRIVATE": 0.0, "NOT_SURE": 0.7},   # visibility
    "PUB":  {"YES": 1.0, "NO": 0.0, "NOT_SURE": 0.6},                          # YES = exposed
    "BAD":  {"YES": 1.0, "SOMETIMES": 0.5, "NO": 0.0, "NOT_SURE": 0.6},        # YES = risky habit
    "GOOD": {"YES": 0.0, "SOMETIMES": 0.5, "NO": 1.0, "NOT_SURE": 0.7},        # YES = protective
}

# category key -> (questionnaire letter, display name)
CATEGORIES = OrderedDict([
    ("profile",     ("A", "Profile Visibility")),
    ("personal",    ("B", "Personal Information")),
    ("location",    ("C", "Location Privacy")),
    ("content",     ("D", "Posts & Content")),
    ("connections", ("E", "Friends / Followers")),
    ("tagging",     ("F", "Tagging & Mentions")),
    ("account",     ("G", "Authentication & Account Security")),
    ("apps",        ("H", "Third-Party Apps")),
    ("social_eng",  ("I", "Messaging & Social Engineering")),
    ("footprint",   ("J", "Digital Footprint")),
])

IMMEDIATE, IMPORTANT, GOOD = "IMMEDIATE", "IMPORTANT", "GOOD PRACTICE"


def _q(qid, cat, text, scale, weight, finding, rec, priority):
    return {"id": qid, "category": cat, "text": text, "scale": scale, "weight": weight,
            "finding": finding, "recommendation": rec, "priority": priority,
            "options": list(SCALES[scale].keys())}


QUESTIONS = [
    # ---- A: Profile Visibility ----
    _q("A1", "profile", "Who can see your profile?", "VIS", 3,
       "Profile is visible beyond trusted contacts",
       "Set profile visibility to Friends or Private unless you intentionally need a public presence.", IMPORTANT),
    _q("A2", "profile", "Can search engines show a link to your profile?", "BAD", 2,
       "Profile can be found through search engines",
       "Turn off search-engine indexing of your profile.", IMPORTANT),
    _q("A3", "profile", "Who can see your friends / followers list?", "VIS", 1,
       "Friends/followers list is visible beyond trusted contacts",
       "Restrict the friends/followers list to Friends or Only Me.", GOOD),
    _q("A4", "profile", "Can strangers find your profile using your phone number or email?", "BAD", 1,
       "Profile is discoverable by phone/email lookup",
       "Limit who can look you up by phone number or email address.", IMPORTANT),
    # ---- B: Personal Information (asks ONLY whether it is visible) ----
    _q("B1", "personal", "Is your phone number publicly visible?", "PUB", 3,
       "Phone number reported as publicly visible",
       "Limit phone-number visibility to 'Only Me' or remove it from your profile.", IMMEDIATE),
    _q("B2", "personal", "Is your personal email address publicly visible?", "PUB", 2,
       "Personal email reported as publicly visible",
       "Hide your personal email or use a separate address for public contact.", IMPORTANT),
    _q("B3", "personal", "Is your full birth date (including year) publicly visible?", "PUB", 2,
       "Full birth date reported as publicly visible",
       "Hide the birth year, or show the date to Friends only.", IMPORTANT),
    _q("B4", "personal", "Is any home-related information (address, neighbourhood, house photos) publicly visible?", "PUB", 3,
       "Home-related information reported as public",
       "Remove or restrict home address details and photos that identify where you live.", IMMEDIATE),
    _q("B5", "personal", "Is your workplace publicly visible?", "PUB", 2,
       "Workplace reported as publicly visible",
       "Limit workplace details to connections, or keep them generic.", IMPORTANT),
    _q("B6", "personal", "Is your school / college publicly visible?", "PUB", 1,
       "Education details reported as publicly visible",
       "Restrict education details to Friends or connections.", GOOD),
    _q("B7", "personal", "Are your relationship or family details publicly visible?", "PUB", 1,
       "Relationship/family details reported as public",
       "Restrict relationship and family details to people you trust.", GOOD),
    # ---- C: Location Privacy ----
    _q("C1", "location", "Do you publicly share your real-time location?", "BAD", 3,
       "Real-time location sharing reported",
       "Avoid publicly broadcasting real-time location; share it only with specific trusted people when needed.", IMMEDIATE),
    _q("C2", "location", "Is geotagging enabled on your posts or camera?", "BAD", 2,
       "Geotagging enabled on posts/photos",
       "Turn off automatic geotagging for posts and in your phone camera settings.", IMPORTANT),
    _q("C3", "location", "Do you make public check-ins at places you visit?", "BAD", 2,
       "Public check-ins reported",
       "Skip public check-ins, or post only after you have left the place.", IMPORTANT),
    _q("C4", "location", "Is your home or workplace location publicly visible?", "PUB", 3,
       "Home/work location reported as publicly visible",
       "Remove precise home/work locations; keep only a city or region if needed.", IMMEDIATE),
    _q("C5", "location", "Do you post travel plans before or during a trip?", "BAD", 2,
       "Travel plans shared before/during trips",
       "Share trip photos after you return instead of while you are away.", IMPORTANT),
    _q("C6", "location", "Do your posts reveal regular routines (gym time, commute, school pick-up)?", "BAD", 1,
       "Posts reveal regular routines",
       "Avoid posting recurring time-and-place patterns.", GOOD),
    # ---- D: Posts & Content ----
    _q("D1", "content", "Who can see your posts by default?", "VIS", 3,
       "Posts are visible beyond trusted contacts",
       "Change the default post audience to Friends, and review audience per post.", IMPORTANT),
    _q("D2", "content", "Do you post photos of children or other people publicly without checking with them or their guardians?", "BAD", 2,
       "Photos of other people/children shared publicly",
       "Get consent before posting others, and avoid public photos of children.", IMPORTANT),
    _q("D3", "content", "Have you posted photos showing badges, documents, vehicle plates or screens?", "BAD", 2,
       "Photos may reveal badges, documents, plates or screens",
       "Crop or blur sensitive items, and delete old photos that show them.", IMPORTANT),
    _q("D4", "content", "Do you upload photos without removing their metadata (EXIF)?", "BAD", 1,
       "Photo metadata may not be removed before upload",
       "Strip EXIF metadata from photos before sharing (see the local metadata tool).", GOOD),
    # ---- E: Friends / Followers ----
    _q("E1", "connections", "Do you accept connection requests from people you do not know?", "BAD", 3,
       "Unknown connection requests are accepted",
       "Verify unfamiliar profiles before accepting connections.", IMMEDIATE),
    _q("E2", "connections", "Can anyone (including strangers) send you friend/follow requests?", "PUB", 2,
       "Anyone can send connection requests",
       "Limit who can send you requests (for example, friends of friends).", IMPORTANT),
    _q("E3", "connections", "Do you regularly review your friends/followers and remove unknown accounts?", "GOOD", 1,
       "Friends/followers are not reviewed regularly",
       "Review your connections every few months and remove accounts you do not recognise.", GOOD),
    _q("E4", "connections", "Are many of your connections people you have never met?", "BAD", 1,
       "Many connections are people you have never met",
       "Prune connections you cannot identify, especially before sharing semi-private content.", IMPORTANT),
    # ---- F: Tagging & Mentions ----
    _q("F1", "tagging", "Can anyone tag you without your approval?", "BAD", 2,
       "Anyone can tag you",
       "Restrict who can tag you to Friends.", IMPORTANT),
    _q("F2", "tagging", "Is tag review (approve tags before they appear) enabled?", "GOOD", 3,
       "Tag review is disabled",
       "Enable tag review so you approve tags before they appear on your profile.", IMPORTANT),
    _q("F3", "tagging", "Do posts you are tagged in appear on your profile automatically?", "BAD", 1,
       "Tagged posts appear on your profile automatically",
       "Require approval before tagged posts appear on your profile.", GOOD),
    _q("F4", "tagging", "Can people outside your connections mention you or message you?", "BAD", 1,
       "Non-connections can mention or message you",
       "Limit mentions and messages to people you are connected with.", GOOD),
    # ---- G: Authentication & Account Security ----
    _q("G1", "account", "Do you use multi-factor authentication (MFA)?", "GOOD", 4,
       "MFA is not (fully) enabled",
       "Enable multi-factor authentication using the strongest supported method (authenticator app or security key).", IMMEDIATE),
    _q("G2", "account", "Do you reuse the same password on more than one account?", "BAD", 3,
       "Password reuse reported",
       "Use a unique password for every account.", IMMEDIATE),
    _q("G3", "account", "Do you use a password manager?", "GOOD", 1,
       "No password manager in use",
       "Use a reputable password manager to create and store unique passwords.", GOOD),
    _q("G4", "account", "Are login alerts enabled?", "GOOD", 2,
       "Login alerts are not enabled",
       "Enable login alerts where available so you notice unfamiliar sign-ins.", IMPORTANT),
    _q("G5", "account", "Have you reviewed your account recovery email/phone recently?", "GOOD", 1.5,
       "Recovery information not reviewed",
       "Check that your recovery email and phone are current and belong to you.", IMPORTANT),
    _q("G6", "account", "Do you review active sessions / logged-in devices?", "GOOD", 1,
       "Active sessions are not reviewed",
       "Review active sessions and log out of devices you no longer use.", GOOD),
    _q("G7", "account", "Do you check for unknown devices or unfamiliar login locations?", "GOOD", 1,
       "Unknown devices/logins are not checked",
       "Periodically check the login-history page and report anything unfamiliar.", GOOD),
    # ---- H: Third-Party Apps ----
    _q("H1", "apps", "Do you review the third-party apps connected to your account?", "GOOD", 3,
       "Connected third-party apps are not reviewed",
       "Review connected apps and revoke the ones you do not need (least privilege).", IMPORTANT),
    _q("H2", "apps", "Do you remove apps and integrations you no longer use?", "GOOD", 2,
       "Unused app integrations are not removed",
       "Remove unused and old integrations.", IMPORTANT),
    _q("H3", "apps", "Do you check what permissions an app asks for before connecting it?", "GOOD", 2,
       "App permissions are not checked before connecting",
       "Read requested permissions and only approve what the app genuinely needs.", IMPORTANT),
    _q("H4", "apps", "Do you use 'Sign in with social account' on many third-party sites?", "BAD", 1,
       "Social sign-in used widely on third-party sites",
       "Prefer separate logins for low-trust sites and review which sites hold social sign-in access.", GOOD),
    # ---- I: Messaging & Social Engineering ----
    _q("I1", "social_eng", "Do you reply to unexpected or suspicious direct messages?", "BAD", 2,
       "Replies to unexpected/suspicious messages reported",
       "Do not engage with unexpected messages; report and block suspicious accounts.", IMPORTANT),
    _q("I2", "social_eng", "Do you click unexpected links sent in messages?", "BAD", 3,
       "Unexpected links are clicked",
       "Do not click unexpected links; open the official site or app yourself instead.", IMMEDIATE),
    _q("I3", "social_eng", "Would you ever share a verification code (OTP) with someone who asks for it?", "BAD", 4,
       "Sharing verification codes reported as possible",
       "Never share verification codes with anyone - no genuine service will ask for them.", IMMEDIATE),
    _q("I4", "social_eng", "Do you share personal details (ID numbers, address, financial info) through messages?", "BAD", 2,
       "Personal details are shared through messages",
       "Avoid sending sensitive details in chats; use verified, official channels.", IMMEDIATE),
    _q("I5", "social_eng", "Do you join giveaways or 'free offers' that ask for logins or personal details?", "BAD", 1,
       "Participation in suspicious giveaways reported",
       "Ignore giveaways that ask for logins, codes or personal details.", IMPORTANT),
    _q("I6", "social_eng", "Do you verify a 'friend' through another channel before acting on an unusual request?", "GOOD", 2,
       "Unusual requests are not verified through a second channel",
       "Confirm unusual requests (money, codes, links) with the person via a different channel.", IMPORTANT),
    # ---- J: Digital Footprint ----
    _q("J1", "footprint", "Do you regularly review your old public posts?", "GOOD", 2,
       "Old posts are not reviewed",
       "Review and delete or restrict old posts that reveal more than you are comfortable with.", IMPORTANT),
    _q("J2", "footprint", "Do you have old or unused social accounts that are still active?", "BAD", 1,
       "Old/unused accounts still active",
       "Delete or lock down accounts you no longer use.", GOOD),
    _q("J3", "footprint", "Do you review your old public comments and profile history?", "GOOD", 1,
       "Old comments/profile history not reviewed",
       "Look through old public comments and past profile information; remove what is no longer appropriate.", GOOD),
    _q("J4", "footprint", "Do you review your privacy settings at least twice a year?", "GOOD", 2,
       "Privacy settings are not reviewed regularly",
       "Schedule a privacy-settings review every 3-6 months, since platforms change defaults.", IMPORTANT),
    _q("J5", "footprint", "Have you checked what a stranger can see on your profile (e.g. 'view as public')?", "GOOD", 1,
       "Public profile view has not been checked",
       "Use 'view as public' (or a logged-out browser) to see what strangers can see.", GOOD),
]

QUESTION_BY_ID = {q["id"]: q for q in QUESTIONS}


class ValidationError(ValueError):
    """Raised for bad input; .errors holds user-safe messages."""
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_answers(answers):
    """Return a cleaned {question_id: OPTION} dict or raise ValidationError."""
    if not isinstance(answers, dict):
        raise ValidationError(["'answers' must be an object of question_id -> answer"])
    if len(answers) > 100:
        raise ValidationError(["Too many answers submitted"])
    errors, clean = [], {}
    for key in answers:
        if key not in QUESTION_BY_ID:
            errors.append("Unknown question id: " + str(key)[:12])
    for q in QUESTIONS:
        if q["id"] not in answers:
            errors.append(f"Missing answer for {q['id']}")
            continue
        raw = answers[q["id"]]
        if not isinstance(raw, str):
            errors.append(f"{q['id']}: answer must be text")
            continue
        val = raw.strip().upper().replace(" ", "_")
        if val not in q["options"]:
            errors.append(f"{q['id']}: answer must be one of {', '.join(q['options'])}")
            continue
        clean[q["id"]] = val
    if errors:
        raise ValidationError(errors)
    return clean


def extreme_answers(kind="best"):
    """Lowest-risk ('best') or highest-risk ('worst') answer set. Used by tests/demo/dataset."""
    pick = min if kind == "best" else max
    return {q["id"]: pick(SCALES[q["scale"]], key=SCALES[q["scale"]].get) for q in QUESTIONS}
