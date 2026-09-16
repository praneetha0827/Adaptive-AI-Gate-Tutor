# AdaptiveAI

AdaptiveAI is an adaptive GATE CSE/IT learning platform. The MVP includes JWT authentication, onboarding and diagnostics, a versioned curriculum, prerequisite-aware topic selection, interactive AI tutoring, scored practice, mastery-based recommendations, gamification, and progress analytics.

## Local setup

1. Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY` and the database password.
2. Start PostgreSQL: `docker compose up -d postgres`.
3. Install frontend dependencies: `cd frontend; npm ci`.
4. Install backend dependencies with a Python 3.12+ environment: `cd backend; python -m pip install -e .[dev]`.
5. Apply migrations: `alembic upgrade head` from `backend`.
6. Run the API: `uvicorn app.main:app --reload --port 8001` from `backend`.
7. Run the web app: `npm run dev` from `frontend`.

Host ports are 5433 (PostgreSQL) and 8001 (API) so they do not collide with other local stacks. API documentation is at `http://localhost:8001/docs` while the backend is running.

For the containerized stack, set `JWT_SECRET_KEY` in `.env`, then run `docker compose up --build`. The backend applies migrations before starting. Open `http://localhost:3000` after the services become healthy.

## Operations

See `docs/operations.md` for deployment, health checks, logs, backups, and recovery guidance.

## Verified curriculum seed

After migrations, run `python scripts/seed_gate_2027.py` from `backend` to add the sourced GATE 2027 CS version and top-level sections. See `docs/curriculum-sourcing.md` before adding detailed curriculum content.
