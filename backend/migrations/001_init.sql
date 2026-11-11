CREATE TABLE IF NOT EXISTS runs (
    id              bigserial PRIMARY KEY,
    title           text        NOT NULL,
    job_description text        NOT NULL,
    method          text        NOT NULL,
    job_skills      text[]      NOT NULL DEFAULT '{}',
    seed_key        text        UNIQUE,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS runs_created_at_idx ON runs (created_at DESC);

CREATE TABLE IF NOT EXISTS results (
    id             bigserial PRIMARY KEY,
    run_id         bigint      NOT NULL REFERENCES runs (id) ON DELETE CASCADE,
    rank           integer     NOT NULL,
    filename       text        NOT NULL,
    score          double precision NOT NULL,
    category       text        NOT NULL,
    matched_skills text[]      NOT NULL DEFAULT '{}',
    missing_skills text[]      NOT NULL DEFAULT '{}',
    education      text[]      NOT NULL DEFAULT '{}',
    experience     text[]      NOT NULL DEFAULT '{}',
    summary        text,
    UNIQUE (run_id, rank)
);
