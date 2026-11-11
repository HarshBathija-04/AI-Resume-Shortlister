from tests.test_parser import _docx_bytes

JOB = "Backend engineer with Python, Flask, SQL and Docker experience building REST APIs."
RESUMES = [
    {"filename": "chef.pdf", "text": "Pastry chef baking bread and cakes for ten years."},
    {"filename": "dev.pdf", "text": "Python developer building Flask REST APIs with SQL and Docker."},
]


def _create(client, **overrides):
    body = {"title": "Backend Engineer", "job_description": JOB, "resumes": RESUMES} | overrides
    return client.post("/api/runs", json=body)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok", "db": "ok"}
    assert res.headers["X-Content-Type-Options"] == "nosniff"


def test_create_and_fetch_run(client):
    res = _create(client)
    assert res.status_code == 201
    run = res.get_json()
    assert [r["filename"] for r in run["results"]] == ["dev.pdf", "chef.pdf"]
    top = run["results"][0]
    assert top["rank"] == 1 and "python" in top["matched_skills"] and top["summary"] == "Summary 0"
    assert run["created_at"].startswith("20")

    assert client.get(f"/api/runs/{run['id']}").get_json()["results"] == run["results"]
    listing = client.get("/api/runs").get_json()
    assert listing["total"] == 1
    assert listing["items"][0]["top_candidate"] == "dev.pdf"
    assert listing["items"][0]["resume_count"] == 2


def test_multipart_upload(client):
    data = {
        "job_description": JOB,
        "resumes": [(_docx_bytes("Python Flask SQL developer"), "dev.docx")],
    }
    res = client.post("/api/runs", data=data, content_type="multipart/form-data")
    assert res.status_code == 201
    assert res.get_json()["title"] == JOB[:120]


def test_rejects_unsupported_upload(client):
    data = {"job_description": JOB, "resumes": [(_docx_bytes("x"), "cv.txt")]}
    res = client.post("/api/runs", data=data, content_type="multipart/form-data")
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "unsupported_file"


def test_validation_errors(client):
    res = _create(client, job_description="too short")
    assert res.status_code == 400
    error = res.get_json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "job_description"
    assert _create(client, resumes=[]).status_code == 400
    assert _create(client, resumes=RESUMES * 7).status_code == 400
    assert client.post("/api/runs", json=["nope"]).status_code == 400


def test_not_found_and_bad_query(client):
    assert client.get("/api/runs/999").get_json()["error"]["code"] == "not_found"
    assert client.get("/api/runs?limit=abc").status_code == 400


def test_csv_export_escapes_formulas(client):
    run = _create(client, resumes=[{"filename": "=cmd.pdf", "text": "Python developer"}]).get_json()
    res = client.get(f"/api/runs/{run['id']}/results.csv")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert "'=cmd.pdf" in res.get_data(as_text=True)


def test_cors_only_allows_frontend(client):
    ok = client.get("/health", headers={"Origin": "http://localhost:5200"})
    assert ok.headers.get("Access-Control-Allow-Origin") == "http://localhost:5200"
    bad = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "Access-Control-Allow-Origin" not in bad.headers
