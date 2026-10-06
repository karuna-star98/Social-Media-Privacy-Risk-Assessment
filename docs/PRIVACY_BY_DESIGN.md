# Privacy by Design in this project
| Principle | How the app applies it |
|---|---|
| Data minimisation | Asks "is your phone number visible?", never for the number; no free-text fields; unknown fields rejected |
| Purpose limitation | Data is used only to compute scores and recommendations; the dataset is fictional |
| Least privilege | No accounts, no scraping, no platform tokens; DB holds scores only |
| Privacy by default | Answers are processed in memory; the schema has no column that could hold sensitive data |
| Transparency | Disclaimers on every result; weights and thresholds visible in code and README |
| User control | Delete endpoint and button; assessments are anonymous |
| Retention limitation | Only scores/finding types stored; delete any time (add a scheduled purge for production) |
| Secure processing | Strict validation, CSP and nosniff headers, escaped report output, rate limiting, generic errors, local-only metadata tool |

**Stored:** assessment_id, overall_score, risk_level, created_at, category scores, finding type/severity/description.
**Never stored:** phone, email, address, birth date, password, exact location, private messages, raw answers.
