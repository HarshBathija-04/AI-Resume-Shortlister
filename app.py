from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_restful import Api, Resource
import csv
import io

from resume_parser import extract_text_from_file
from nlp_utils import preprocess_text
from matcher import (
    extract_skills,
    extract_education,
    extract_experience,
    rank_resumes,
    match_category,
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
api = Api(app)

LAST_RESULTS = None


def _build_results_from_texts(resume_texts, filenames, job_description, method):
    if not job_description:
        raise ValueError("Job description is required.")
    if not resume_texts:
        raise ValueError("At least one resume is required.")

    job_clean = preprocess_text(job_description)
    resume_clean_texts = [preprocess_text(t) for t in resume_texts]

    scores = rank_resumes(resume_clean_texts, job_clean, method)
    job_skills = sorted(extract_skills(job_clean))

    results = []
    matched_total = 0
    missing_total = 0

    for idx, filename in enumerate(filenames):
        resume_clean = resume_clean_texts[idx]
        resume_raw = resume_texts[idx]

        resume_skills = sorted(extract_skills(resume_clean))
        matched = sorted(set(resume_skills).intersection(job_skills))
        missing = sorted(set(job_skills) - set(resume_skills))

        matched_total += len(matched)
        missing_total += len(missing)

        results.append(
            {
                "filename": filename,
                "score": scores[idx],
                "category": match_category(scores[idx]),
                "matched_skills": matched,
                "missing_skills": missing,
                "education": extract_education(resume_raw),
                "experience": extract_experience(resume_raw),
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)

    score_labels = [r["filename"] for r in results]
    score_values = [r["score"] for r in results]

    return {
        "job_description": job_description,
        "method": method,
        "job_skills": job_skills,
        "results": results,
        "score_labels": score_labels,
        "score_values": score_values,
        "skill_coverage": {
            "matched": matched_total,
            "missing": missing_total,
        },
    }


def _build_results_from_files(resume_files, job_description, method):
    resume_texts = []
    filenames = []

    for file_obj in resume_files:
        if not file_obj or not file_obj.filename:
            continue
        text = extract_text_from_file(file_obj)
        resume_texts.append(text or "")
        filenames.append(file_obj.filename)

    return _build_results_from_texts(resume_texts, filenames, job_description, method)


@app.route("/")
def index():
    error = request.args.get("error")
    return render_template("index.html", error=error)


@app.route("/upload-resumes", methods=["POST"])
def upload_resumes():
    global LAST_RESULTS

    resume_files = request.files.getlist("resumes")
    job_description = request.form.get("job_description", "")
    method = "semantic"

    try:
        LAST_RESULTS = _build_results_from_files(resume_files, job_description, method)
    except Exception as exc:
        return redirect(url_for("index", error=str(exc)))

    return redirect(url_for("results"))


@app.route("/results")
def results():
    if not LAST_RESULTS:
        return redirect(url_for("index", error="No results available. Upload resumes first."))
    return render_template("results.html", **LAST_RESULTS)


@app.route("/download")
def download():
    if not LAST_RESULTS:
        return redirect(url_for("index", error="No results available."))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "filename",
            "score",
            "category",
            "matched_skills",
            "missing_skills",
            "education",
            "experience",
        ]
    )

    for row in LAST_RESULTS["results"]:
        writer.writerow(
            [
                row["filename"],
                row["score"],
                row["category"],
                ", ".join(row["matched_skills"]),
                ", ".join(row["missing_skills"]),
                "; ".join(row["education"]),
                "; ".join(row["experience"]),
            ]
        )

    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)

    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="ranked_results.csv",
    )


class MatchResource(Resource):
    def post(self):
        global LAST_RESULTS

        if request.is_json:
            payload = request.get_json(silent=True) or {}
            job_description = payload.get("job_description", "")
            method = "semantic"
            resume_items = payload.get("resumes", [])

            resume_texts = []
            filenames = []
            for item in resume_items:
                resume_texts.append(item.get("text", ""))
                filenames.append(item.get("filename", "resume"))

            try:
                LAST_RESULTS = _build_results_from_texts(
                    resume_texts, filenames, job_description, method
                )
            except Exception as exc:
                return {"error": str(exc)}, 400

            return LAST_RESULTS, 200

        resume_files = request.files.getlist("resumes")
        job_description = request.form.get("job_description", "")
        method = "semantic"

        try:
            LAST_RESULTS = _build_results_from_files(resume_files, job_description, method)
        except Exception as exc:
            return {"error": str(exc)}, 400

        return LAST_RESULTS, 200


class ResultsResource(Resource):
    def get(self):
        return LAST_RESULTS or {}


api.add_resource(MatchResource, "/api/match")
api.add_resource(ResultsResource, "/api/results")


if __name__ == "__main__":
    app.run(debug=True)
