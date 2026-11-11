"""Postgres access. Every connection is pinned to this app's own schema (DB_SCHEMA)."""

import os
import re
from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def schema_name():
    schema = os.environ.get("DB_SCHEMA", "resume_shortlister")
    # The schema name is interpolated into SQL identifiers, so only allow a safe identifier.
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", schema):
        raise RuntimeError("DB_SCHEMA must be a lowercase SQL identifier")
    return schema


def _database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


@contextmanager
def connect():
    # shortcut: one connection per request, fine for one small gunicorn instance;
    # add psycopg_pool if traffic grows.
    with psycopg.connect(
        _database_url(),
        options=f"-c search_path={schema_name()}",
        row_factory=dict_row,
        connect_timeout=10,
    ) as conn:
        yield conn


def migrate():
    """Create the schema if needed and apply any migrations/*.sql not yet recorded."""
    schema = schema_name()
    with psycopg.connect(_database_url(), autocommit=True) as conn:
        conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
    with connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " name text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
        )
        applied = {r["name"] for r in conn.execute("SELECT name FROM schema_migrations")}
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in applied:
                continue
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,))
            print(f"applied migration {path.name}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    migrate()
