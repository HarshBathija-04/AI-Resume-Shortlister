import json
from types import SimpleNamespace

import groq

import ai

CANDIDATES = [
    {"text": "Python dev", "score": 80.0, "matched_skills": ["python"], "missing_skills": []},
    {"text": "Chef", "score": 20.0, "matched_skills": [], "missing_skills": ["python"]},
]


def _fake_groq(monkeypatch, content=None, error=None):
    def create(**kwargs):
        if error:
            raise error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(groq, "Groq", lambda **kwargs: client)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")


def test_without_key_returns_none(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    assert ai.summarize_candidates("job", CANDIDATES) == [None, None]


def test_aligns_summaries_by_index(monkeypatch):
    payload = {
        "summaries": [{"index": 1, "summary": " Not a fit. "}, {"index": 0, "summary": "Strong."}, "junk"]
    }
    _fake_groq(monkeypatch, content=json.dumps(payload))
    assert ai.summarize_candidates("job", CANDIDATES) == ["Strong.", "Not a fit."]


def test_invalid_json_degrades_gracefully(monkeypatch):
    _fake_groq(monkeypatch, content="not json")
    assert ai.summarize_candidates("job", CANDIDATES) == [None, None]


def test_api_error_degrades_gracefully(monkeypatch):
    _fake_groq(monkeypatch, error=groq.APIConnectionError(request=None))
    assert ai.summarize_candidates("job", CANDIDATES) == [None, None]
