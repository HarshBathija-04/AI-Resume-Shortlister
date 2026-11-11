import os
import re
import threading
import urllib.request
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        # Lookarounds instead of \b so skills ending in symbols (c++, c#) still match.
        if re.search(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", text):
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


# Same all-MiniLM-L6-v2 model the app used via sentence-transformers, as a quantized ONNX export:
# ~60 MB RAM instead of ~1 GB for torch, so it fits a 512 MB Render instance.
MODEL_DIR = Path(os.environ.get("MODEL_DIR", Path(__file__).parent / "models" / "all-MiniLM-L6-v2"))
MODEL_FILES = {
    "model.onnx": "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/main/onnx/model_quantized.onnx",
    "tokenizer.json": "https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/main/tokenizer.json",
}
_MODEL = None
_MODEL_LOCK = threading.Lock()


def ensure_model():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in MODEL_FILES.items():
        target = MODEL_DIR / name
        if not target.exists():
            tmp = target.with_suffix(".part")
            urllib.request.urlretrieve(url, tmp)  # noqa: S310 - fixed https URLs above
            tmp.replace(target)


def _load_model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            _MODEL = _create_model()
    return _MODEL


def _create_model():
    import onnxruntime as ort
    from tokenizers import Tokenizer

    ensure_model()
    options = ort.SessionOptions()
    options.enable_cpu_mem_arena = False
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(str(MODEL_DIR / "model.onnx"), options, providers=["CPUExecutionProvider"])
    tokenizer = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
    tokenizer.no_padding()  # single unpadded inputs, so mean pooling sees only real tokens
    tokenizer.enable_truncation(256)  # sentence-transformers max_seq_length for this model
    return session, tokenizer


def _embed(text):
    session, tokenizer = _load_model()
    ids = np.array([tokenizer.encode(text).ids], dtype=np.int64)
    feeds = {"input_ids": ids, "attention_mask": np.ones_like(ids), "token_type_ids": np.zeros_like(ids)}
    vector = session.run(None, feeds)[0].mean(axis=1)[0]  # mean pooling
    return vector / (np.linalg.norm(vector) or 1.0)


def _semantic_similarity(resume_texts, job_text):
    job_emb = _embed(job_text)
    return [float(_embed(text) @ job_emb) for text in resume_texts]


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
