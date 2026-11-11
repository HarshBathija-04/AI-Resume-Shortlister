import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Tests use their own schema and never call Groq.
os.environ["DB_SCHEMA"] = "resume_shortlister_test"
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/portfolio")
os.environ["GROQ_API_KEY"] = ""
os.environ["FRONTEND_URL"] = "http://localhost:5200"

SAMPLES = Path(__file__).resolve().parents[1] / "sample_resumes"


@pytest.fixture
def client(monkeypatch):
    import shortlist
    from app import create_app
    from db import connect, migrate

    migrate()
    with connect() as conn:
        conn.execute("TRUNCATE runs RESTART IDENTITY CASCADE")
    monkeypatch.setattr(
        shortlist, "summarize_candidates", lambda jd, cands: [f"Summary {i}" for i in range(len(cands))]
    )
    app = create_app()
    app.config["RATELIMIT_ENABLED"] = False
    return app.test_client()
