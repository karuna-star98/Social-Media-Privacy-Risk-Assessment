# Test plan (run: `python -m pytest -v`)
"Actual / Pass" = result of the build-time run (56 of 56 passed in the build sandbox). Re-run on your machine and screenshot `pytest -v`.

| ID | Scenario | Input | Expected | Actual / Pass |
|---|---|---|---|---|
| T01 | Fully private profile | safest answer to all 51 | 0, LOW, no findings | Pass |
| T02 | Fully public profile | riskiest answers | 100, CRITICAL | Pass |
| T03-T10 | Public phone / email / birthday / location / real-time check-ins / travel plans / workplace / education | one risky answer on a perfect profile | exactly that finding; only its category > 0 | Pass |
| T11-T20 | Public posts / unknown connections / tag review off / MFA off / login alerts off / password reuse / apps unreviewed / risky links / old posts / settings unreviewed | same pattern | same | Pass |
| T21 | Category score | all "Personal" answers worst | personal = 100, others 0 | Pass |
| T22 | Overall score | same input | overall = 15 (15% weight); custom weights -> 25 | Pass |
| T23-T25 | Boundaries 20/21, 40/41, 70/71 | classify_risk | LOW/MODERATE, MODERATE/HIGH, HIGH/CRITICAL | Pass |
| T26 | Recommendations | MFA off, phone public, J5 no | IMMEDIATE, IMMEDIATE, GOOD PRACTICE | Pass |
| T27 | Improvement simulation | demo profile + 10 fixes | lower score, reduction > 15, disclaimer | Pass |
| T28 | Database save | POST then GET | scores match, 10 categories | Pass |
| T29 | Sensitive data not stored | dump DB, inspect columns | no answers, no sensitive column names | Pass |
| T30 | Report generation | GET report | contains id, disclaimer, checklist | Pass |

## Security & privacy tests (extra)
Validation (non-object, empty, unknown ids, bad values, wrong types) -> 400 · raw `phone_number` field rejected · HTML in report escaped (XSS) · rate limit -> 429 · CSP / nosniff / no-store headers · 16 KB payload cap -> 413 · malformed JSON gives no stack trace · delete removes record · invalid id format -> 400 · bad weights rejected · dataset has 1,000+ fictional rows · metadata tool strips EXIF.
