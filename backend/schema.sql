-- schema.sql — source of truth DDL for Neon Postgres.
-- Apply once: psql "$DATABASE_URL" -f schema.sql

CREATE TABLE IF NOT EXISTS urls (
    id              BIGSERIAL PRIMARY KEY,
    -- short_code is nullable transiently: auto-generated codes are Base62(id),
    -- which isn't known until the row's id exists (see app/base62.py + app/crud.py).
    -- Custom aliases are written directly on insert instead.
    short_code      TEXT,
    long_url        TEXT NOT NULL,
    is_custom_alias BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ
);

-- Unique + indexed as specified, via a partial index (NULL allowed only
-- during the brief insert -> compute -> update window for auto codes).
-- Case-sensitive on purpose: Base62 uses upper+lower+digits, so collation
-- must not fold case.
CREATE UNIQUE INDEX IF NOT EXISTS idx_urls_short_code
    ON urls (short_code)
    WHERE short_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS clicks (
    id          BIGSERIAL PRIMARY KEY,
    url_id      BIGINT NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
    clicked_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    device_type TEXT,
    location    TEXT,
    referrer    TEXT
);

-- FK lookups and time-bucketed aggregates both hit these.
CREATE INDEX IF NOT EXISTS idx_clicks_url_id ON clicks (url_id);
CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks (clicked_at);
