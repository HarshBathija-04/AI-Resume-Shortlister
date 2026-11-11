import pytest

from matcher import (
    extract_education,
    extract_experience,
    extract_skills,
    match_category,
    rank_resumes,
)
from nlp_utils import preprocess_text

JOB = "Backend engineer: Python, Flask, SQL and Docker. Build REST APIs and deploy to AWS."
STRONG = "Python developer. Built Flask REST APIs backed by PostgreSQL SQL, shipped with Docker on AWS."
WEAK = "Pastry chef with ten years of experience baking bread, cakes and desserts."


def test_extract_skills_uses_word_boundaries_and_phrases():
    skills = extract_skills("Expert in JavaScript, machine learning and C++.")
    assert {"javascript", "machine learning", "c++"} <= skills
    assert "java" not in skills


def test_extract_education_and_experience():
    text = "B.Tech in Computer Science, Pune University\nProfessional Experience\nI have 5 years in Python"
    assert extract_education(text) == ["B.Tech in Computer Science, Pune University"]
    assert extract_experience(text) == ["Professional Experience", "5 years"]


@pytest.mark.parametrize(
    "score, category", [(90, "Excellent"), (85, "Excellent"), (70, "Good"), (40, "Average"), (39.9, "Poor")]
)
def test_match_category_thresholds(score, category):
    assert match_category(score) == category


@pytest.mark.parametrize("method", ["tfidf", "semantic"])
def test_rank_resumes_prefers_the_relevant_resume(method):
    strong, weak = rank_resumes(
        [preprocess_text(STRONG), preprocess_text(WEAK)], preprocess_text(JOB), method
    )
    assert strong > weak
    assert 0 <= weak <= 100 and 0 <= strong <= 100


def test_rank_resumes_rejects_empty_job():
    with pytest.raises(ValueError):
        rank_resumes(["python"], "   ", "tfidf")


def test_preprocess_text_strips_noise():
    assert (
        preprocess_text("Email me at a@b.com or visit https://x.io! Running APIs")
        == "email visit running apis"
    )
