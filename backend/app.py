"""
FILE: backend/app.py
PURPOSE: Flask application factory. Serves the REST API and the static frontend.
Run from the project root:  python -m backend.app
"""
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from .config import Config
from .models import database as db
from .routes.api import bp
from .services.questionnaire import ValidationError
from .utils.rate_limiter import RateLimiter

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def create_app(overrides=None):
    app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")
    app.config.from_object(Config)
    app.config.update(overrides or {})
    Path(app.config["DB_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    c = db.connect(app.config["DB_PATH"]); db.init_db(c); c.close()
    limiter = RateLimiter(app.config["RATE_LIMIT_PER_MIN"])
    app.register_blueprint(bp)

    @app.before_request
    def rate_limit():
        if request.path.startswith("/api/") and not limiter.allow(request.remote_addr or "?"):
            r = jsonify(error="rate_limited", message="Too many requests - slow down.")
            r.status_code, r.headers["Retry-After"] = 429, "60"
            return r

    @app.after_request
    def security_headers(resp):
        style = "'self' 'unsafe-inline'" if request.path.endswith("/report") else "'self'"
        resp.headers["Content-Security-Policy"] = (
            f"default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com; "
            f"style-src {style}; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        if request.path.startswith("/api/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    @app.errorhandler(ValidationError)
    def bad_input(err):
        return jsonify(error="validation_failed", details=err.errors), 400

    @app.errorhandler(LookupError)
    def not_found_record(_):
        return jsonify(error="not_found", message="Assessment not found"), 404

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="not_found"), 404

    @app.errorhandler(413)
    def too_big(_):
        return jsonify(error="payload_too_large"), 413

    @app.errorhandler(Exception)
    def server_error(err):
        if hasattr(err, "code") and err.code and err.code < 500:       # normal HTTP errors
            return jsonify(error=err.name.lower().replace(" ", "_")), err.code
        app.logger.exception("Unhandled error")                        # details only in server log
        return jsonify(error="server_error", message="Something went wrong"), 500

    @app.get("/")
    def home():
        return send_from_directory(FRONTEND, "index.html")

    return app


if __name__ == "__main__":
    create_app().run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
