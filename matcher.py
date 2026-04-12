from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

SKILLS = [
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "html",
    "css",
    "react",
    "node",
    "flask",
    "django",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "machine learning",
    "data science",
    "nlp",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
]

EDU_KEYWORDS = [
    "bachelor",
    "master",
    "phd",
    "doctorate",
    "associate",
    "mba",
    "b.sc",
    "m.sc",
    "b.tech",
    "m.tech",
    "university",
    "college",
    "institute",
    "diploma",
]

EXPERIENCE_KEYWORDS = [
    "experience",
    "work history",
    "employment",
    "professional experience",
]


def extract_skills(text):
    text = text.lower()
    found = set()

    for skill in SKILLS:
        if " " in skill:
            if skill in text:
                found.add(skill)
        else:
            if re.search(r"\b" + re.escape(skill) + r"\b", text):
                found.add(skill)

    return found


def extract_education(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    results = []

    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in EDU_KEYWORDS):
            results.append(line)

    return _unique_trimmed(results)


def extract_experience(text):
    results = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in EXPERIENCE_KEYWORDS):
            results.append(line)

    year_matches = re.findall(r"\b\d+\+?\s+years?\b", text.lower())
    for match in year_matches:
        results.append(match)

    return _unique_trimmed(results)


def _unique_trimmed(items):
    cleaned = []
    seen = set()
    for item in items:
        value = " ".join(item.split())
        if value and value not in seen:
            cleaned.append(value)
            seen.add(value)
    return cleaned


def _tfidf_similarity(resume_texts, job_text):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=8000)
    vectors = vectorizer.fit_transform([job_text] + resume_texts)
    job_vec = vectors[0]
    resume_vecs = vectors[1:]
    scores = cosine_similarity(resume_vecs, job_vec)
    return scores.flatten().tolist()


def _semantic_similarity(resume_texts, job_text):
    try:
        from sentence_transformers import SentenceTransformer, util
    except Exception as exc:
        raise RuntimeError(
            "Sentence Transformers is not available. Install sentence-transformers to use semantic matching."
        ) from exc

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode([job_text] + resume_texts, convert_to_tensor=True)
    job_emb = embeddings[0]
    resume_embs = embeddings[1:]
    scores = util.cos_sim(resume_embs, job_emb)
    return scores.cpu().numpy().flatten().tolist()


def rank_resumes(resume_texts, job_text, method):
    if not job_text.strip():
        raise ValueError("Job description is empty after preprocessing.")

    if method == "semantic":
        raw_scores = _semantic_similarity(resume_texts, job_text)
    else:
        raw_scores = _tfidf_similarity(resume_texts, job_text)

    return [round(score * 100, 2) for score in raw_scores]


def match_category(score):
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 40:
        return "Average"
    return "Poor"
