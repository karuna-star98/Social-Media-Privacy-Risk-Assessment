"""
FILE: backend/routes/api.py
PURPOSE: REST API.  No user accounts => no login. Each assessment id is an unguessable random
token (capability URL); only someone holding it can read/delete that record. Answers are
processed in memory and NEVER stored. Errors are generic JSON (no stack traces).
"""
import re, uuid
from flask import Blueprint, Response, current_app, g, jsonify, request
from ..models import database as db
from ..services.questionnaire import QUESTIONS, CATEGORIES, ValidationError
from ..services.assessment_engine import run_assessment
from ..services.recommendation_engine import generate_recommendations
from ..services.improvement_simulator import simulate_improvement, list_presets
from ..services.report_generator import render_report_html
from ..services.analytics import synthetic_dashboard
from ..services.content import CHECKLIST, DISCLAIMER, demo_profile_answers

bp = Blueprint("api", __name__, url_prefix="/api")
ID_RE = re.compile(r"^PRA-[0-9a-f]{12}$")


def conn():
    if "db" not in g:
        g.db = db.connect(current_app.config["DB_PATH"])
    return g.db


@bp.teardown_app_request
def _close(_exc):
    c = g.pop("db", None)
    if c is not None:
        c.close()


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError(["Request body must be a JSON object"])
    return data


def valid_id(aid):
    if not ID_RE.match(aid):
        raise ValidationError(["Invalid assessment id format"])
    return aid


def load_or_404(aid):
    rec = db.get_assessment(conn(), valid_id(aid))
    if rec is None:
        raise LookupError
    return rec


@bp.get("/questionnaire")
def questionnaire():
    cats = [{"key": k, "letter": v[0], "name": v[1],
             "questions": [{"id": q["id"], "text": q["text"], "options": q["options"]}
                           for q in QUESTIONS if q["category"] == k]} for k, v in CATEGORIES.items()]
    return jsonify({"total_questions": len(QUESTIONS), "categories": cats, "disclaimer": DISCLAIMER})


@bp.get("/demo-profile")
def demo_profile():
    return jsonify({"note": "Fictional demo answers", "answers": demo_profile_answers()})


@bp.post("/assessment")
def create_assessment():
    out = run_assessment(body().get("answers"))
    aid = "PRA-" + uuid.uuid4().hex[:12]
    created = db.save_assessment(conn(), aid, out)         # scores + finding types only
    out.update(assessment_id=aid, created_at=created, disclaimer=DISCLAIMER)
    out.pop("weights", None)
    return jsonify(out), 201


@bp.get("/assessment/<aid>")
def get_assessment(aid):
    return jsonify({**load_or_404(aid), "disclaimer": DISCLAIMER})


@bp.get("/assessment/<aid>/recommendations")
def get_recommendations(aid):
    rec = load_or_404(aid)
    return jsonify({"assessment_id": aid, "recommendations": generate_recommendations(rec["findings"])})


@bp.get("/assessment/<aid>/report")
def get_report(aid):
    rec = load_or_404(aid)
    html = render_report_html(rec, generate_recommendations(rec["findings"]))
    resp = Response(html, mimetype="text/html")
    if request.args.get("download") == "1":
        resp.headers["Content-Disposition"] = f'attachment; filename="privacy-report-{aid}.html"'
    return resp


@bp.delete("/assessment/<aid>")
def delete_assessment(aid):
    if not db.delete_assessment(conn(), valid_id(aid)):
        raise LookupError
    return jsonify({"deleted": aid})


@bp.post("/assessment/simulate-improvement")
def simulate():
    data = body()
    return jsonify(simulate_improvement(data.get("answers"), data.get("changes")))


@bp.get("/improvement-options")
def improvement_options():
    return jsonify({"options": list_presets()})


@bp.get("/dashboard/stats")
def dashboard_stats():
    return jsonify({"synthetic": synthetic_dashboard(current_app.config["DATASET_PATH"]),
                    "live": db.live_stats(conn()),
                    "note": "Synthetic aggregate uses fictional records only."})


@bp.get("/privacy-checklist")
def checklist():
    return jsonify({"title": "Social Media Privacy Checklist", "items": CHECKLIST})
