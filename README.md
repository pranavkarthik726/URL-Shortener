# URL Shortener

A Bitly-style URL shortener: shorten a URL (auto-generated or custom alias),
redirect visitors while logging click analytics (device, location, time),
and support link expiry (TTL).

## Architecture

- **Backend:** Python + FastAPI, raw SQL via `psycopg3` (no ORM) — hosted on Railway.
- **Database:** PostgreSQL — hosted on Neon.
- **Frontend:** React + Vite, single page, no router library — hosted on Vercel.

The redirect endpoint (`GET /{short_code}`) lives on the backend, so shortened
links point at the **backend's** domain (Railway), not the frontend's.

## Design decisions

- **Base62(auto-increment id) for generated codes.** No collision handling
  is needed (unlike a random/hash-based scheme), since ids are unique by
  construction. The id isn't known until insert, so auto-generated rows are
  inserted with `short_code = NULL`, then updated to `Base62(id)` — see
  `backend/app/crud.py:insert_auto_url`. On the rare chance a previously
  claimed custom alias already equals a later id's Base62 code, the insert
  falls back to `f"{code}-{id}"`, which is guaranteed unique with no retry loop.
- **Postgres over a document store.** `urls` and `clicks` are relational
  (one url has many clicks) and click logging benefits from FK/ACID
  guarantees — a click can't reference a url row that doesn't exist.
- **`short_code` has a unique (partial) B-tree index**, so every redirect is
  an O(log n) index lookup instead of a table scan.
- **TTL is checked lazily on read**, not via a cron sweep: `GET /{short_code}`
  compares `expires_at` to `now()` at request time. This trades "dead rows"
  lingering in `urls` after expiry for zero scheduling infrastructure —
  acceptable given "no Redis, no background workers" is a project constraint.
- **Click count is `COUNT(*)` over `clicks`, not a denormalized counter
  column.** The analytics endpoint already has to query `clicks` (indexed on
  `url_id`) for the device/location/time breakdowns, so total clicks reuses
  that same path. A denormalized counter would need a second write
  (`UPDATE urls SET click_count = click_count + 1`) on every click, adding
  write contention on a hot row and a risk of drift if that write is ever
  skipped — not worth it at this project's scale.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
copy .env.example .env        # then fill in DATABASE_URL with a real Neon connection string
psql "%DATABASE_URL%" -f schema.sql   # apply the schema once
uvicorn app.main:app --reload --port 8000
```

API docs are then available at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env        # defaults to http://127.0.0.1:8000, matches the backend above
npm run dev
```

Open `http://127.0.0.1:5173`.

> Local dev intentionally uses `127.0.0.1` rather than `localhost` in every
> URL/env default (`BASE_URL`, `FRONTEND_ORIGIN`, `VITE_API_BASE_URL`). On
> some machines `localhost` resolves to the IPv6 loopback (`::1`) first,
> while a bare `uvicorn` only binds the IPv4 loopback — the browser then
> fails to even reach the backend, which shows up as a misleading CORS
> error in devtools. `127.0.0.1` sidesteps the ambiguity entirely.

## Deployment (manual steps)

1. **Neon:** create a project, copy the pooled connection string (with
   `sslmode=require`), and apply `backend/schema.sql` against it.
2. **Railway:** create a service from this repo with **Root Directory =
   `backend`**. Set env vars `DATABASE_URL` (the Neon string), `BASE_URL`
   (the Railway-assigned public URL), and `FRONTEND_ORIGIN` (the Vercel URL
   from step 3, once known). Railway will use `backend/Procfile` to start
   `uvicorn`.
3. **Vercel:** create a project from this repo with **Root Directory =
   `frontend`** (Vite preset is auto-detected). Set env var
   `VITE_API_BASE_URL` to the Railway backend's public URL, then deploy.
4. Go back to Railway and set `FRONTEND_ORIGIN` to the deployed Vercel URL
   (needed for CORS), and redeploy the backend.

## API reference

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/api/shorten` | `{ "long_url": "...", "custom_alias"?: "...", "expires_at"?: "YYYY-MM-DD" }` | `201 { "short_code": "...", "short_url": "..." }`; `409` if alias taken |
| `GET` | `/{short_code}` | — | `302` redirect to `long_url`; `404` if unknown; `410` if expired |
| `GET` | `/api/analytics/{short_code}` | — | `200` `{ short_code, long_url, created_at, expires_at, total_clicks, device_breakdown, location_breakdown, clicks_over_time }`; `404` if unknown |
