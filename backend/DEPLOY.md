# Deploying to FastAPI Cloud

## Prerequisites

- [FastAPI Cloud](https://fastapicloud.com) account
- `pip install "fastapi[standard]"` or `uv add "fastapi[standard]"` (installs the CLI)
- A PostgreSQL database URL (e.g. from [Neon](https://neon.tech) — already configured in `.env`)

## One-time setup

### 1. Log in

```bash
fastapi login
```

### 2. Set the application directory in the dashboard

LiquidityLens is a monorepo. After creating your app in the dashboard:

- Go to **App → Settings → Application Directory**
- Enter `backend`
- Click **Update**

This tells FastAPI Cloud to build and run from the `backend/` subdirectory.

### 3. Set environment variables

Run these from inside the `backend/` directory (or set them in the dashboard):

```bash
# Required
fastapi env set DATABASE_URL "postgresql+psycopg://user:pass@host/dbname?sslmode=require"
fastapi env set DATABASE_SYNC_URL "postgresql+psycopg://user:pass@host/dbname?sslmode=require"

# CORS: set to your deployed frontend URL (comma-separated if multiple)
fastapi env set ALLOWED_ORIGINS "https://your-frontend.vercel.app"

# Explanation provider (keep as 'none' for deterministic fallback)
fastapi env set LLM_EXPLANATION_PROVIDER "none"
fastapi env set LLM_EXPLANATION_ENABLED "false"

# Optional
fastapi env set APP_ENV "production"
fastapi env set APP_NAME "liquiditylens-api"
```

> **Tip:** Use `fastapi env set --secret DATABASE_URL "..."` to mark the DB URL as a secret.

### 4. Deploy

```bash
cd backend
fastapi deploy
```

The app will be available at `https://<your-app-name>.fastapicloud.dev`.

## What happens on startup

The `lifespan` event in `app/main.py` automatically:

1. Runs `alembic upgrade head` — creates or migrates all database tables.
2. Seeds 6 demo users with deterministic UUIDs (idempotent — safe to re-run).

No manual migration step is needed.

## Verifying the deployment

```bash
# Health check
curl https://<your-app-name>.fastapicloud.dev/api/v1/health

# Readiness (checks DB connectivity)
curl https://<your-app-name>.fastapicloud.dev/api/v1/readiness

# Interactive API docs
open https://<your-app-name>.fastapicloud.dev/docs
```

## Local development

```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Or with Docker Compose from the repo root:

```bash
docker-compose up --build
```

## Notes

- The app expects `alembic.ini` to be in the working directory (`backend/`). FastAPI Cloud sets the application directory as the working directory, so this resolves correctly.
- `ALLOWED_ORIGINS` is comma-separated. Add your frontend URL after deploying the frontend.
- Demo user UUIDs are fixed (`00000000-0000-0000-0000-00000000000{1-6}`). The frontend maps demo roles to these IDs in `src/lib/api.ts → DEMO_USERS`.
