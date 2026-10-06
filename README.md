# Social Media Privacy Risk Assessment Framework

> This project is designed for defensive cybersecurity and privacy education.
> It uses synthetic or voluntarily provided assessment responses and does not
> scrape, track, or profile real social-media users.

## Overview
A privacy-risk assessment platform. A user answers a **51-question, 10-category** questionnaire about their social-media settings and habits. The app returns a **0-100 Privacy Risk Score** (higher = more exposure), a level (LOW / MODERATE / HIGH / CRITICAL), category scores, findings, prioritised recommendations, a "what if I improve?" simulator, a dashboard and a printable report.

## Problem Statement
Oversharing (public phone/birthday/location), weak account controls (no MFA, reused passwords) and risky habits (accepting unknown requests, clicking links) enable doxxing, impersonation and social engineering. People rarely review their settings in a structured way.

## Objectives
Assess exposure without collecting the exposed data itself · score it transparently · coach with concrete fixes · stay privacy-preserving.

## Cybersecurity Relevance
Privacy engineering, security awareness, digital-risk management, identity protection, GRC (risk scoring, controls, documentation), IAM hygiene (MFA, sessions, app grants), application security (validation, CSP, rate limiting). Roles: Cybersecurity / Privacy / GRC / SOC Analyst, IAM Analyst, Security Awareness Specialist, Privacy Engineer.

## Privacy vs Security
**Privacy** = how personal information is collected, shared and exposed. **Security** = protecting accounts/systems from unauthorised access. A user with MFA and a unique password (good security) can still publish their phone number, birthday and live location (poor privacy). *Strong security != strong privacy.*

## Features
51-question questionnaire · input validation · feature extraction · 10 category scores · configurable weights · findings engine · recommendation engine (IMMEDIATE / IMPORTANT / GOOD PRACTICE) · improvement simulator (21 presets) · radar + bar charts · dashboard (6 charts) · HTML/PDF report · printable checklist · 1,000-record synthetic dataset · local photo-metadata tool · 56 automated tests.

## Architecture
```
User -> Questionnaire -> Input Validation -> Feature Extraction -> Category Analysis
     -> Scoring Engine -> Overall Score -> Risk Classification -> Findings
     -> Recommendations -> Dashboard -> Report
```
One Flask process serves the API and the static frontend. SQLite stores scores + finding types only.

## Technology Stack
Python 3.10+, Flask, SQLite, HTML/CSS/vanilla JS, Chart.js (CDN), Pillow, pytest. Chosen for beginners: one command to run, no build step. A FastAPI + React version is a good "v2".

## Folder structure
| Folder | Purpose |
|---|---|
| `backend/app.py` | Flask app factory, security headers, rate limiting, error handlers |
| `backend/routes/` | REST API |
| `backend/models/` | SQLite schema + queries |
| `backend/services/` | questionnaire, assessment / scoring / findings / recommendation / simulator engines, report, analytics |
| `backend/utils/` | rate limiter, local metadata viewer/cleaner |
| `frontend/` | index, assessment, dashboard pages + css/js |
| `data/` | dataset generator + generated CSV (local DB is git-ignored) |
| `tests/` | automated tests |
| `docs/` | threat model, privacy-by-design, GitHub guide, career kit, screenshot checklist |
| `reports/`, `screenshots/` | your exported reports / proof screenshots |

## Privacy Questionnaire
**A** Profile Visibility (4) · **B** Personal Information (7) · **C** Location (6) · **D** Posts & Content (4) · **E** Friends/Followers (4) · **F** Tagging (4) · **G** Account Security (7) · **H** Third-Party Apps (4) · **I** Messaging & Social Engineering (6) · **J** Digital Footprint (5). Answers are fixed options (PUBLIC/FRIENDS/PRIVATE or YES/NO/SOMETIMES/NOT SURE). **No free text; no phone, email, address, birth-date or password fields.**

## Risk Categories & Scoring
Each answer maps to a risk 0.0-1.0; each question has a weight. Category score = weighted mean x 100. Overall = sum(category score x category weight).

| Category | Weight | Category | Weight |
|---|---|---|---|
| Profile | 10% | Account Security | 15% |
| Personal Info | 15% | Third-Party Apps | 5% |
| Location | 15% | Social Engineering | 10% |
| Content | 10% | Digital Footprint | 5% |
| Connections | 10% | Tagging | 5% |

Levels: 0-20 LOW · 21-40 MODERATE · 41-70 HIGH · 71-100 CRITICAL. Weights are configurable (`calculate_privacy_risk(features, weights)`). **Weights and thresholds are educational assumptions and must be validated before any professional risk decision.**

## Privacy Findings · Recommendation Engine · Improvement Simulator
A finding is raised when an answer's risk >= 0.5 (NOT SURE counts and is flagged), ranked by `risk x weight`. Each finding maps to a recommendation with a priority. The simulator re-scores answers after applying presets (`enable_mfa`, `phone_private`, ...) and shows before / after / risk reduction. **It is a framework simulation, not a guarantee of real-world safety.**

## Digital Footprint · Social Engineering · Account Security
- *Footprint*: active (deliberately shared) vs passive (collected through activity, depending on the service). Only self-reported practices are assessed.
- *Social engineering*: public employer, college, travel and family details can make scams more believable. The tool teaches defences (verify via a second channel, never share OTPs) and contains **no attack scripts**.
- *Account security*: MFA, unique passwords, password manager, login alerts, recovery info, sessions, unknown devices. Overlaps with privacy but is not identical.

## Privacy Dashboard · Report
`/dashboard.html`: score, level, high-risk categories, recommendations, controls enabled + 6 charts. Population charts use synthetic data. Report: `/api/assessment/<id>/report` (HTML; print -> PDF); it contains no sensitive data.

## Privacy by Design
Data minimisation · purpose limitation · privacy by default · user control (delete) · retention limitation · secure processing · transparency. Details: `docs/PRIVACY_BY_DESIGN.md`.

## Installation & Usage
```bash
cd Social-Media-Privacy-Risk-Assessment
python -m venv venv
source venv/bin/activate             # Windows: venv\Scripts\activate
pip install -r requirements.txt
python data/generate_dataset.py      # optional: a CSV is already included
python -m backend.app                # serves API + frontend
# open http://127.0.0.1:5000 -> Start Privacy Assessment
# (or click "Load fictional demo profile") -> score -> charts -> simulator -> report
python -m backend.demo               # optional terminal demo
```
Local photo-metadata tool (nothing uploaded): `python -m backend.utils.metadata_tool view photo.jpg` / `strip photo.jpg clean.jpg`.

## API Documentation
| Endpoint | Purpose |
|---|---|
| `GET /api/questionnaire` | questions + options |
| `POST /api/assessment` | body `{"answers":{"A1":"PUBLIC",...}}` (all 51) -> `201` score, level, categories, findings, recommendations, id; `400` if invalid |
| `GET /api/assessment/{id}` | stored scores + findings (`400` bad id, `404` unknown) |
| `GET /api/assessment/{id}/recommendations` | prioritised recommendations |
| `GET /api/assessment/{id}/report[?download=1]` | HTML report |
| `POST /api/assessment/simulate-improvement` | `{"answers":{...},"changes":["enable_mfa"]}` -> before / after / reduction (answers not stored) |
| `GET /api/improvement-options` | simulator presets |
| `GET /api/dashboard/stats` | synthetic aggregates + live counts |
| `GET /api/privacy-checklist` | 18-item checklist |
| `DELETE /api/assessment/{id}` | delete stored result |

*Authentication*: no user accounts; each id (`PRA-` + 12 random hex chars) is an unguessable capability token. *Rate limit*: 120 req/min/IP -> `429`. *Errors*: generic JSON, no stack traces.

## Testing · Security & Privacy Testing
```bash
python -m pytest -v
```
56 tests: T01-T30 (private/public profile, each risky setting, category and overall scoring, boundaries 20/40/70, recommendations, simulator, DB save, sensitive data not stored, report) plus input validation, rejection of raw sensitive fields, XSS escaping, rate limiting, security headers, oversized payloads, no stack-trace leaks, deletion, dataset validity, metadata stripping. See `docs/TEST_PLAN.md`.

## Results
Fictional demo profile: **63/100 HIGH -> 27/100 MODERATE** after 12 improvements (36-point reduction). Synthetic dataset: 1,000 records, mean 51.5 (84 LOW / 236 MODERATE / 446 HIGH / 234 CRITICAL).

## Limitations
Self-reported answers can be wrong · weights and thresholds are assumptions, not calibrated · platform settings change · not validated against real incidents · English only.

## Future Improvements
Platform-specific checklists · organisational policies · awareness quizzes · privacy maturity scoring · teen/family modules · employee training reports · anonymous trend analysis · weight calibration against expert ratings · localisation and accessibility · report comparison over time · client-side/local-only mode. (No scraping or invasive monitoring.)

## Screenshots
See `docs/SCREENSHOT_CHECKLIST.md`; save images into `screenshots/`.

## Learning Outcomes
Risk-scoring design · privacy engineering · secure API design · validation · threat modelling · testing · GRC thinking · security-awareness communication.

## Ethical Disclaimer
Educational, defensive use only. Use only with your own self-reported answers or the fictional demo data. Do not use it to profile, track or investigate other people. Results are estimates, not guarantees.

## Author
`<Your Name>` · `<LinkedIn>` · `<GitHub>`
