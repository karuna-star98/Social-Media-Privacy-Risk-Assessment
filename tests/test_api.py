"""API, database, report, privacy and security tests (T28-T30 + extras)."""
import sqlite3
import pytest
from backend.services.report_generator import render_report_html


def post(client, answers):
    return client.post("/api/assessment", json={"answers": answers})


def test_T28_database_save_and_fetch(client, worst):
    r = post(client, worst)
    assert r.status_code == 201
    aid = r.get_json()["assessment_id"]
    got = client.get(f"/api/assessment/{aid}").get_json()
    assert got["overall_score"] == 100 and got["risk_level"] == "CRITICAL" and len(got["category_scores"]) == 10
    recs = client.get(f"/api/assessment/{aid}/recommendations").get_json()["recommendations"]
    assert recs and recs[0]["priority"] == "IMMEDIATE"


def test_T29_sensitive_data_not_stored(client, app, worst):
    post(client, worst)
    con = sqlite3.connect(app.config["DB_PATH"])
    dump = "\n".join(con.iterdump())
    assert "NOT_SURE" not in dump and '"answers"' not in dump
    banned = ("phone", "email", "address", "birth", "password", "latitude", "longitude", "message", "answer")
    for (table,) in con.execute("select name from sqlite_master where type='table'"):
        for col in con.execute(f"pragma table_info({table})"):
            assert not any(b in col[1].lower() for b in banned), (table, col[1])


def test_T30_report_generation(client, worst):
    aid = post(client, worst).get_json()["assessment_id"]
    r = client.get(f"/api/assessment/{aid}/report?download=1")
    assert r.status_code == 200 and aid in r.get_data(as_text=True)
    html = r.get_data(as_text=True)
    assert "not a guarantee" in html and "Privacy checklist" in html
    assert "attachment" in r.headers["Content-Disposition"]


def test_report_escapes_html():                       # XSS protection
    a = {"assessment_id": "<script>x</script>", "created_at": "now", "overall_score": 5, "risk_level": "LOW",
         "category_scores": {"profile": 5}, "findings": [{"severity": "LOW", "description": "<img onerror=1>"}]}
    out = render_report_html(a, [])
    assert "<script>x" not in out and "&lt;script&gt;" in out and "<img onerror" not in out


@pytest.mark.parametrize("payload", [None, [], {"answers": []}, {"answers": {}}, {"answers": {"Z9": "YES"}}])
def test_input_validation(client, payload):
    r = client.post("/api/assessment", json=payload)
    assert r.status_code == 400 and r.get_json()["error"] == "validation_failed"


def test_invalid_answer_value_and_type(client, best):
    best["B1"] = "<script>"; best["B2"] = 5
    r = post(client, best)
    assert r.status_code == 400 and "<script>" not in r.get_data(as_text=True)


def test_extra_unknown_field_rejected(client, best):
    best["phone_number"] = "555-1234"                  # the API must refuse raw sensitive values
    assert post(client, best).status_code == 400


def test_bad_ids_and_404(client):
    assert client.get("/api/assessment/not-an-id").status_code == 400
    assert client.get("/api/assessment/PRA-000000000000").status_code == 404
    assert client.get("/api/does-not-exist").status_code == 404


def test_data_deletion(client, best):
    aid = post(client, best).get_json()["assessment_id"]
    assert client.delete(f"/api/assessment/{aid}").status_code == 200
    assert client.get(f"/api/assessment/{aid}").status_code == 404


def test_simulate_endpoint(client):
    from backend.services.content import demo_profile_answers
    r = client.post("/api/assessment/simulate-improvement",
                    json={"answers": demo_profile_answers(), "changes": ["enable_mfa", "phone_private"]})
    assert r.status_code == 200 and r.get_json()["risk_reduction"] > 0


def test_dashboard_checklist_questionnaire(client):
    s = client.get("/api/dashboard/stats").get_json()
    assert s["synthetic"]["records"] >= 1000 and "live" in s
    assert len(client.get("/api/privacy-checklist").get_json()["items"]) == 18
    assert client.get("/api/questionnaire").get_json()["total_questions"] >= 40


def test_rate_limiting(tmp_path):
    from backend.app import create_app
    c = create_app({"DB_PATH": str(tmp_path / "r.db"), "RATE_LIMIT_PER_MIN": 3}).test_client()
    codes = [c.get("/api/privacy-checklist").status_code for _ in range(5)]
    assert codes[:3] == [200] * 3 and codes[3] == 429


def test_security_headers_and_oversize(client):
    h = client.get("/api/privacy-checklist").headers
    assert "default-src 'self'" in h["Content-Security-Policy"] and h["X-Content-Type-Options"] == "nosniff"
    assert h["Cache-Control"] == "no-store"
    assert client.post("/api/assessment", data="x" * 20000, content_type="application/json").status_code == 413


def test_no_server_internals_leak(client):
    r = client.post("/api/assessment", data="{bad json", content_type="application/json")
    assert r.status_code == 400 and "Traceback" not in r.get_data(as_text=True)


def test_synthetic_dataset_is_valid():
    import csv, pathlib
    rows = list(csv.DictReader(open(pathlib.Path("data/social_media_privacy_assessments.csv"))))
    assert len(rows) >= 1000 and all(r["profile_id"].startswith("SYN-") for r in rows)
    assert {"phone_public", "mfa_enabled", "risk_score", "risk_level"} <= set(rows[0])
    assert all(0 <= int(r["risk_score"]) <= 100 for r in rows)


def test_metadata_tool_strips_exif(tmp_path):
    from PIL import Image
    from backend.utils.metadata_tool import view_metadata, strip_metadata
    img = Image.new("RGB", (4, 4), "red"); ex = Image.Exif(); ex[271] = "FictionalCam"
    src = tmp_path / "a.jpg"; img.save(src, exif=ex)
    assert view_metadata(str(src)).get("Make") == "FictionalCam"
    assert "Make" not in view_metadata(strip_metadata(str(src), str(tmp_path / "b.jpg")))
