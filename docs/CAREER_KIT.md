# Resume / LinkedIn / Interview kit

## Resume bullets
- Built a privacy-risk assessment framework (Python/Flask/SQLite) scoring 51 self-reported social-media settings across 10 categories into a 0-100 risk score with configurable weights and LOW-CRITICAL classification.
- Implemented privacy-by-design controls (data minimisation, no PII fields, score-only storage, deletion endpoint, CSP, rate limiting) and 56 automated functional and security tests.
- Developed a recommendation engine, "what-if" improvement simulator and analytics dashboard over a 1,000-record synthetic dataset, demonstrating a 36-point modelled risk reduction for a demo profile.

## 2-line description
Defensive privacy-risk framework that turns self-reported social-media settings into category scores, prioritised fixes and a what-if simulator. Privacy-by-design: no scraping, no PII collected, synthetic data only.

## LinkedIn project text
I built the **Social Media Privacy Risk Assessment Framework**, a defensive cybersecurity project that helps people understand their online exposure without collecting any of it. Users answer 51 questions about visibility, location sharing, account security, third-party apps, social-engineering habits and digital footprint; the app produces a 0-100 risk score, category analysis, prioritised recommendations, an improvement simulator, a dashboard and a printable report. It follows privacy-by-design (only scores are stored), uses synthetic data, and is covered by 56 automated tests. Skills: Python, Flask, SQLite, risk scoring, GRC concepts, threat modelling, secure API design, security awareness. #Cybersecurity #Privacy #GRC #PrivacyByDesign

## Skills demonstrated
Cybersecurity · Privacy risk assessment · Privacy by design · Digital-footprint analysis · Social-engineering awareness · Risk scoring · Python · Data analytics · Security awareness · GRC concepts · REST API design · Input validation · Testing · Threat modelling

## Interview prep
Your brief already contains the 10 questions and answers (starting with "Explain your project"). They match this implementation. Add these concrete details so you sound like the builder:
- **Scoring:** answer -> risk 0-1, per-question weights, weighted mean per category, weighted sum overall; boundaries tested at 20/21, 40/41, 70/71.
- **Data minimisation:** the API rejects unknown fields and free text; the DB schema has no column that could hold PII; tests inspect the DB.
- **Simulator:** presets override answers and re-run the same engine, so before/after are consistent.
- **Limitations:** self-reported, uncalibrated weights; next step is calibrating against expert ratings.
- **Security:** CSP, nosniff, escaped report output, rate limiting, generic errors, capability-style IDs.
