"""Idempotent demo data: runs the real pipeline over the bundled sample resumes."""

from pathlib import Path

from dotenv import load_dotenv

import shortlist
from db import connect, migrate
from resume_parser import extract_text_from_path

SAMPLES = Path(__file__).parent / "sample_resumes"

DATA_ANALYST_JD = """Junior Data Analyst

We are hiring a Junior Data Analyst to turn raw business data into clear, decision-ready insight.

Responsibilities:
Clean, join and analyse datasets using SQL and Python (pandas, numpy)
Build dashboards and recurring reports for sales and operations teams
Run exploratory analysis and A/B test readouts; explain findings to non-technical stakeholders
Maintain data quality checks and document metric definitions

Required Skills:
SQL (joins, window functions), Python with pandas and numpy
Excel and a BI tool such as Power BI or Tableau
Statistics fundamentals and clear written communication

Nice to have:
Machine learning basics, data science coursework, Git
"""

ACCOUNT_EXEC_JD = """Account Executive (B2B SaaS)

Own the full sales cycle for mid-market accounts, from prospecting to close.

Responsibilities:
Prospect and qualify new business through outbound and inbound pipeline
Run discovery calls and product demos; build business cases with champions
Negotiate contracts and close deals against a quarterly quota
Keep CRM records accurate and forecast pipeline weekly

Requirements:
2+ years of experience in B2B sales or account management
Track record of meeting or exceeding quota
Strong negotiation, presentation and relationship-building skills
Experience with Salesforce or HubSpot CRM
"""

DEMO_RUNS = [
    {
        "seed_key": "demo-swe-intern",
        "title": "Software Engineer Intern",
        "jd_file": "SampleJobDescription.docx",
        "resumes": [
            "SampleResume.pdf",
            "Software Engineer.pdf",
            "Software Engineers.pdf",
            "Data Scientist-1.pdf",
            "Data Scientist-2.pdf",
            "junior data analyst.pdf",
            "web & graphic designer.pdf",
            "sales representative.pdf",
        ],
    },
    {
        "seed_key": "demo-data-analyst",
        "title": "Junior Data Analyst",
        "jd": DATA_ANALYST_JD,
        "resumes": [
            "junior data analyst.pdf",
            "junior data analysts.pdf",
            "Data Scientist-1.pdf",
            "Data Scientist-2.pdf",
            "Senior accountants.pdf",
            "Content creators.pdf",
        ],
    },
    {
        "seed_key": "demo-account-exec",
        "title": "Account Executive (B2B SaaS)",
        "jd": ACCOUNT_EXEC_JD,
        "resumes": [
            "Accoount executive.pdf",
            "Accoount executives.pdf",
            "sales representative.pdf",
            "sales representatives.pdf",
            "Senior accountants.pdf",
            "Software Engineer.pdf",
        ],
    },
]


def seed():
    with connect() as conn:
        existing = {
            r["seed_key"] for r in conn.execute("SELECT seed_key FROM runs WHERE seed_key IS NOT NULL")
        }
    for demo in DEMO_RUNS:
        if demo["seed_key"] in existing:
            continue
        jd = demo.get("jd") or extract_text_from_path(SAMPLES / demo["jd_file"])
        resumes = [(name, extract_text_from_path(SAMPLES / name)) for name in demo["resumes"]]
        run_id = shortlist.create_run(demo["title"], jd, resumes, seed_key=demo["seed_key"])
        print(f"seeded {demo['seed_key']} as run {run_id}")


if __name__ == "__main__":
    load_dotenv()
    migrate()
    seed()
