"""
FILE: backend/models/database.py
PURPOSE: Privacy-first SQLite storage. Stores ONLY scores, finding types and timestamps.
Never stored: phone, email, address, birth date, passwords, exact location, messages, or raw answers.
"""
import sqlite3
from datetime import datetime, timezone
from ..services.recommendation_engine import recommendation_catalog

SCHEMA = """
CREATE TABLE IF NOT EXISTS ASSESSMENTS(
  assessment_id TEXT PRIMARY KEY, overall_score INTEGER NOT NULL,
  risk_level TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS CATEGORY_SCORES(
  category_score_id INTEGER PRIMARY KEY AUTOINCREMENT,
  assessment_id TEXT NOT NULL REFERENCES ASSESSMENTS(assessment_id) ON DELETE CASCADE,
  category TEXT NOT NULL, score INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS FINDINGS(
  finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
  assessment_id TEXT NOT NULL REFERENCES ASSESSMENTS(assessment_id) ON DELETE CASCADE,
  category TEXT NOT NULL, finding_type TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS RECOMMENDATIONS(
  recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  finding_type TEXT NOT NULL UNIQUE, recommendation TEXT NOT NULL, priority TEXT NOT NULL);
"""


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn):
    conn.executescript(SCHEMA)
    conn.executemany("INSERT OR IGNORE INTO RECOMMENDATIONS(finding_type,recommendation,priority) VALUES(?,?,?)",
                     recommendation_catalog())
    conn.commit()


def save_assessment(conn, assessment_id, out):
    created = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with conn:
        conn.execute("INSERT INTO ASSESSMENTS VALUES(?,?,?,?)",
                     (assessment_id, out["overall_score"], out["risk_level"], created))
        conn.executemany("INSERT INTO CATEGORY_SCORES(assessment_id,category,score) VALUES(?,?,?)",
                         [(assessment_id, c, s) for c, s in out["category_scores"].items()])
        conn.executemany("INSERT INTO FINDINGS(assessment_id,category,finding_type,severity,description) VALUES(?,?,?,?,?)",
                         [(assessment_id, f["category"], f["finding_type"], f["severity"], f["description"])
                          for f in out["findings"]])
    return created


def get_assessment(conn, assessment_id):
    row = conn.execute("SELECT * FROM ASSESSMENTS WHERE assessment_id=?", (assessment_id,)).fetchone()
    if not row:
        return None
    cats = conn.execute("SELECT category,score FROM CATEGORY_SCORES WHERE assessment_id=? ORDER BY category_score_id",
                        (assessment_id,)).fetchall()
    finds = conn.execute("SELECT category,finding_type,severity,description FROM FINDINGS WHERE assessment_id=? ORDER BY finding_id",
                         (assessment_id,)).fetchall()
    return {**dict(row), "category_scores": {c["category"]: c["score"] for c in cats},
            "findings": [dict(f) for f in finds]}


def delete_assessment(conn, assessment_id):
    with conn:
        return conn.execute("DELETE FROM ASSESSMENTS WHERE assessment_id=?", (assessment_id,)).rowcount > 0


def live_stats(conn):
    total, avg = conn.execute("SELECT COUNT(*), AVG(overall_score) FROM ASSESSMENTS").fetchone()
    dist = {r[0]: r[1] for r in conn.execute("SELECT risk_level, COUNT(*) FROM ASSESSMENTS GROUP BY risk_level")}
    return {"total": total, "avg_score": round(avg or 0, 1), "level_distribution": dist}
