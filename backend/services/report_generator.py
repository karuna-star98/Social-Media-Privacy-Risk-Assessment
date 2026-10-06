"""
FILE: backend/services/report_generator.py
PURPOSE: Self-contained, printable HTML report (print -> "Save as PDF"). Contains NO sensitive data.
All dynamic values are HTML-escaped to prevent XSS.
"""
from html import escape as e
from .questionnaire import CATEGORIES
from .content import CHECKLIST, DISCLAIMER

CSS = """body{font-family:Arial,sans-serif;max-width:820px;margin:2rem auto;color:#1b2430;padding:0 1rem}
h1{border-bottom:3px solid #1f4e79;padding-bottom:.4rem}h2{color:#1f4e79;margin-top:1.6rem}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:.4rem;text-align:left}
.score{font-size:2.4rem;font-weight:bold}.note{background:#fff4d6;padding:.8rem;border-radius:6px}
.LOW{color:#1e8449}.MODERATE{color:#b7950b}.HIGH{color:#d35400}.CRITICAL{color:#c0392b}
@media print{.noprint{display:none}}"""


def render_report_html(a, recommendations):
    cats = "".join(f"<tr><td>{e(CATEGORIES[c][1])}</td><td>{int(s)}/100</td></tr>"
                   for c, s in a["category_scores"].items() if c in CATEGORIES)
    finds = "".join(f"<li><b>{e(f['severity'])}</b> - {e(f['description'])}</li>" for f in a["findings"][:10]) \
        or "<li>No significant findings.</li>"
    recs = "".join(f"<tr><td>{e(r['priority'])}</td><td>{e(r['recommendation'])}</td></tr>" for r in recommendations) \
        or "<tr><td colspan=2>None</td></tr>"
    prio = "".join(f"<li>{e(r['recommendation'])}</li>" for r in recommendations if r["priority"] == "IMMEDIATE") \
        or "<li>No immediate actions.</li>"
    check = "".join(f"<li>&#9633; {e(c)}</li>" for c in CHECKLIST)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Privacy Assessment {e(a['assessment_id'])}</title><style>{CSS}</style></head><body>
<h1>Social Media Privacy Risk Assessment Report</h1>
<p><b>Assessment ID:</b> {e(a['assessment_id'])}<br><b>Date:</b> {e(a['created_at'])}</p>
<p class="score">{int(a['overall_score'])}/100 - <span class="{e(a['risk_level'])}">{e(a['risk_level'])}</span></p>
<p>Higher score = higher assessed exposure/risk.</p>
<h2>Category scores</h2><table><tr><th>Category</th><th>Score</th></tr>{cats}</table>
<h2>Top findings</h2><ul>{finds}</ul>
<h2>Priority actions</h2><ul>{prio}</ul>
<h2>Security recommendations</h2><table><tr><th>Priority</th><th>Recommendation</th></tr>{recs}</table>
<h2>Privacy checklist</h2><ul style="list-style:none">{check}</ul>
<h2>Disclaimer</h2><p class="note">{e(DISCLAIMER)}</p>
<p class="noprint">Tip: press Ctrl+P (Cmd+P) and choose "Save as PDF".</p>
</body></html>"""
