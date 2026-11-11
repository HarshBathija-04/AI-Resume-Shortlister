"""Shortlisting pipeline (matching logic unchanged from the original app) and run persistence."""

import os

from ai import summarize_candidates
from db import connect
from matcher import (
    extract_education,
    extract_experience,
    extract_skills,
    match_category,
    rank_resumes,
)
from nlp_utils import preprocess_text


def match_method():
    method = os.environ.get("MATCH_METHOD", "semantic")
    return method if method in ("semantic", "tfidf") else "semantic"


def build_results(resume_texts, filenames, job_description, method):
    if not job_description:
        raise ValueError("Job description is required.")
    if not resume_texts:
        raise ValueError("At least one resume is required.")

    job_clean = preprocess_text(job_description)
    resume_clean_texts = [preprocess_text(t) for t in resume_texts]

    scores = rank_resumes(resume_clean_texts, job_clean, method)
    # Skills come from raw text: preprocessing strips symbols and lemmatizes (c++ -> c, pandas -> panda).
    job_skills = sorted(extract_skills(job_description))

    results = []
    for idx, filename in enumerate(filenames):
        resume_skills = extract_skills(resume_texts[idx])
        results.append(
            {
                "filename": filename,
                "score": scores[idx],
                "category": match_category(scores[idx]),
                "matched_skills": sorted(resume_skills.intersection(job_skills)),
                "missing_skills": sorted(set(job_skills) - resume_skills),
                "education": extract_education(resume_texts[idx]),
                "experience": extract_experience(resume_texts[idx]),
                "text": resume_texts[idx],
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return job_skills, results


def default_title(job_description):
    first_line = next((ln.strip() for ln in job_description.splitlines() if ln.strip()), "")
    first_line = first_line.removeprefix("Job Title:").strip()
    return (first_line or "Untitled role")[:120]


def create_run(title, job_description, resumes, seed_key=None):
    """resumes: list of (filename, text). Returns the stored run id."""
    method = match_method()
    filenames = [name for name, _ in resumes]
    texts = [text for _, text in resumes]
    job_skills, results = build_results(texts, filenames, job_description, method)
    summaries = summarize_candidates(job_description, results)

    with connect() as conn:
        run_id = conn.execute(
            "INSERT INTO runs (title, job_description, method, job_skills, seed_key)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (title or default_title(job_description), job_description, method, job_skills, seed_key),
        ).fetchone()["id"]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO results (run_id, rank, filename, score, category, matched_skills,"
                " missing_skills, education, experience, summary)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        run_id,
                        rank,
                        r["filename"],
                        r["score"],
                        r["category"],
                        r["matched_skills"],
                        r["missing_skills"],
                        r["education"][:20],
                        r["experience"][:20],
                        summary,
                    )
                    for rank, (r, summary) in enumerate(zip(results, summaries, strict=True), start=1)
                ],
            )
    return run_id


def get_run(run_id):
    with connect() as conn:
        run = conn.execute(
            "SELECT id, title, job_description, method, job_skills, created_at FROM runs WHERE id = %s",
            (run_id,),
        ).fetchone()
        if not run:
            return None
        run["results"] = conn.execute(
            "SELECT rank, filename, score, category, matched_skills, missing_skills,"
            " education, experience, summary FROM results WHERE run_id = %s ORDER BY rank",
            (run_id,),
        ).fetchall()
    run["skill_coverage"] = {
        "matched": sum(len(r["matched_skills"]) for r in run["results"]),
        "missing": sum(len(r["missing_skills"]) for r in run["results"]),
    }
    return run


def list_runs(limit, offset):
    with connect() as conn:
        total = conn.execute("SELECT count(*) AS n FROM runs").fetchone()["n"]
        items = conn.execute(
            "SELECT r.id, r.title, r.method, r.created_at,"
            " count(x.id) AS resume_count, max(x.score) AS top_score,"
            " (SELECT filename FROM results WHERE run_id = r.id AND rank = 1) AS top_candidate"
            " FROM runs r LEFT JOIN results x ON x.run_id = r.id"
            " GROUP BY r.id ORDER BY r.created_at DESC, r.id DESC LIMIT %s OFFSET %s",
            (limit, offset),
        ).fetchall()
    return {"items": items, "total": total}
