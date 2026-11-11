"""JSON API for AI Resume Shortlister."""

import csv
import io
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import BaseModel, Field, ValidationError, field_validator
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

import shortlist
from db import connect
from resume_parser import extract_text_from_file

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MAX_RESUMES = 12
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = (".pdf", ".docx")


class JSONProvider(DefaultJSONProvider):
    sort_keys = False

    @staticmethod
    def default(o):
        return o.isoformat() if isinstance(o, datetime) else DefaultJSONProvider.default(o)


def _csv_cell(value):
    # Neutralise spreadsheet formula injection from user-controlled filenames/text.
    value = str(value)
    return "'" + value if value[:1] in ("=", "+", "-", "@") else value


class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        super().__init__(message)
        self.status, self.code, self.message, self.details = status, code, message, details


class ResumeIn(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    text: str = Field(max_length=100_000)


class RunIn(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    job_description: str = Field(min_length=30, max_length=20_000)
    resumes: list[ResumeIn] = Field(min_length=1, max_length=MAX_RESUMES)

    @field_validator("title", "job_description", mode="before")
    @classmethod
    def strip(cls, value):
        return value.strip() or None if isinstance(value, str) else value


def _resumes_from_upload():
    files = [f for f in request.files.getlist("resumes") if f and f.filename]
    if len(files) > MAX_RESUMES:
        raise ApiError(400, "too_many_files", f"Upload at most {MAX_RESUMES} resumes per run.")
    resumes = []
    for file_obj in files:
        name = os.path.basename(file_obj.filename)
        if not name.lower().endswith(ALLOWED_EXTENSIONS):
            raise ApiError(400, "unsupported_file", f"{name}: only PDF and DOCX files are supported.")
        data = file_obj.read()
        if len(data) > MAX_FILE_BYTES:
            raise ApiError(400, "file_too_large", f"{name}: files must be 5 MB or smaller.")
        try:
            text = extract_text_from_file(io.BytesIO(data), name)
        except Exception:
            raise ApiError(422, "unreadable_file", f"{name}: the file could not be read.") from None
        resumes.append({"filename": name, "text": text})
    return resumes


def _parse_run_input():
    if request.is_json:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            raise ApiError(400, "invalid_json", "Request body must be a JSON object.")
    else:
        payload = {
            "title": request.form.get("title"),
            "job_description": request.form.get("job_description", ""),
            "resumes": _resumes_from_upload(),
        }
    try:
        return RunIn.model_validate(payload)
    except ValidationError as exc:
        details = [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        raise ApiError(400, "validation_error", "Some fields are invalid.", details) from None


def _get_run_or_404(run_id):
    run = shortlist.get_run(run_id)
    if not run:
        raise ApiError(404, "not_found", "Run not found.")
    return run


def create_app():
    app = Flask(__name__)
    app.json = JSONProvider(app)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # Render sits behind one proxy

    origins = [o.strip() for o in os.environ.get("FRONTEND_URL", "").split(",") if o.strip()]
    CORS(app, origins=origins or ["http://localhost:5200"])
    limiter = Limiter(get_remote_address, app=app, default_limits=["120 per minute"], storage_uri="memory://")

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.errorhandler(ApiError)
    def handle_api_error(exc):
        body = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details:
            body["error"]["details"] = exc.details
        return jsonify(body), exc.status

    @app.errorhandler(HTTPException)
    def handle_http_error(exc):
        code = "rate_limited" if exc.code == 429 else (exc.name or "error").lower().replace(" ", "_")
        message = (
            "Too many requests. Please wait a minute and try again." if exc.code == 429 else exc.description
        )
        return jsonify({"error": {"code": code, "message": message}}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        log.exception("Unhandled error")
        return jsonify({"error": {"code": "internal_error", "message": "Something went wrong."}}), 500

    @app.get("/health")
    @limiter.exempt
    def health():
        try:
            with connect() as conn:
                conn.execute("SELECT 1")
        except Exception:
            log.exception("Health check DB failure")
            return jsonify({"status": "error", "db": "error"}), 503
        return jsonify({"status": "ok", "db": "ok"})

    @app.get("/api/runs")
    def runs_index():
        try:
            limit = min(max(int(request.args.get("limit", 20)), 1), 100)
            offset = max(int(request.args.get("offset", 0)), 0)
        except ValueError:
            raise ApiError(400, "validation_error", "limit and offset must be integers.") from None
        return jsonify(shortlist.list_runs(limit, offset))

    @app.post("/api/runs")
    @limiter.limit("5 per minute; 30 per hour")  # matching is CPU heavy and each run calls Groq
    def runs_create():
        data = _parse_run_input()
        try:
            run_id = shortlist.create_run(
                data.title, data.job_description, [(r.filename, r.text) for r in data.resumes]
            )
        except ValueError as exc:
            raise ApiError(400, "validation_error", str(exc)) from None
        return jsonify(_get_run_or_404(run_id)), 201

    @app.get("/api/runs/<int:run_id>")
    def runs_show(run_id):
        return jsonify(_get_run_or_404(run_id))

    @app.get("/api/runs/<int:run_id>/results.csv")
    def runs_csv(run_id):
        run = _get_run_or_404(run_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "rank",
                "filename",
                "score",
                "category",
                "matched_skills",
                "missing_skills",
                "education",
                "experience",
                "ai_summary",
            ]
        )
        for row in run["results"]:
            cells = [
                row["rank"],
                row["filename"],
                row["score"],
                row["category"],
                ", ".join(row["matched_skills"]),
                ", ".join(row["missing_skills"]),
                "; ".join(row["education"]),
                "; ".join(row["experience"]),
                row["summary"] or "",
            ]
            writer.writerow([_csv_cell(c) for c in cells])
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f'attachment; filename="shortlist-run-{run_id}.csv"'},
        )

    return app


app = create_app()
