# Operations Guide

## Production deployment

Deploy the frontend and backend as separate services backed by managed PostgreSQL. Terminate TLS at the platform load balancer or reverse proxy. Configure `DATABASE_URL`, a strong unique `JWT_SECRET_KEY`, `CORS_ORIGINS`, and the optional `OPENAI_API_KEY` through the deployment platform's secret store.

Before releasing, run `alembic upgrade head` as a one-time release step. Run at least two backend replicas only after moving rate limiting to a shared store such as Redis; the in-process limiter is intentionally a single-instance safety guard.

## Health and logs

Use `GET /health` for liveness checks and `GET /ready` for readiness checks; the latter returns `503` until PostgreSQL is reachable. Capture structured application logs and the `X-Request-ID` response header in your monitoring tool. Alert on elevated `5xx`, repeated AI provider failures, and migration failures. Never log access tokens, passwords, raw API keys, or full learner messages by default.

## Backups and recovery

Use managed PostgreSQL automated daily backups with point-in-time recovery. Retain backups for at least 30 days and test a restore quarterly in a separate environment. The restore procedure is: provision a new database, restore the selected backup, run schema verification, and smoke-test `/health`, login, and a read-only dashboard request before switching traffic.

## Local containers

Create `.env` from `.env.example`, set `JWT_SECRET_KEY`, then run `docker compose up --build`. The backend container applies pending migrations before starting Uvicorn, and Compose waits for the API readiness check before starting the frontend.
