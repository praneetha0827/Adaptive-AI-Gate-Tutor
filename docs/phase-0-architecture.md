# AdaptiveAI — Phase 0 Architecture

## 1. Product boundary

AdaptiveAI is a multi-user adaptive learning platform for GATE CSE/IT. Its value is not conversational AI alone: it maintains a durable, auditable student knowledge model and uses it to select instruction, practice, revision, and recommendations.

The initial product is a modular monolith with a Next.js web client, FastAPI API, PostgreSQL database, and one AI provider behind an adapter. Each module has clear service boundaries but deploys as one backend application.

## 2. High-level system architecture

```text
Browser (Next.js)
        |
        | HTTPS + JWT
        v
FastAPI modular monolith
  |- Auth and profiles
  |- Curriculum
  |- Learning paths and progress
  |- Assessment and scoring
  |- Knowledge model and recommendations
  |- Gamification and analytics
  `- AI orchestration
        |                    |
        v                    v
 PostgreSQL             AI provider API
```

The browser never communicates with an AI provider or PostgreSQL directly. Backend services enforce authorization, update learning state, and decide what structured context is passed to an AI provider.

## 3. Detailed backend architecture

```text
API router -> request schema -> application service -> repository -> PostgreSQL
                                    |
                                    +-> domain policy (mastery, XP, recommendations)
                                    |
                                    `-> AI orchestrator -> provider adapter
```

* **API routers** authenticate requests, validate input, and serialize responses.
* **Application services** own use cases such as submitting an answer or starting a tutor session.
* **Domain policies** are deterministic pure logic for mastery, scoring, XP, badges, and recommendations where possible.
* **Repositories** are the only layer that reads or writes persistence models.
* **AI orchestrator** builds constrained context, requests structured output, validates it, and sends it to the relevant service. It cannot write database rows.

Use synchronous HTTP requests for the MVP. Add a background worker only when generation, analytics aggregation, or notifications make request latency unacceptable.

## 4. Frontend architecture

Use Next.js App Router, TypeScript, Tailwind CSS, and a small typed API client.

* Public routes: landing, sign up, sign in.
* Protected routes: onboarding, diagnostic, dashboard, learn, quiz, progress, badges, profile.
* Server rendering is used for public shells and initial protected pages where useful; interactive learning and quiz screens are client components.
* Client state is limited to UI/session state. PostgreSQL remains the source of truth for learning progress.
* API response types are shared through generated OpenAPI types or a small manually maintained type layer—not duplicated loosely across pages.

The initial dashboard should prioritize the recommended next action, weak topics, current goal, and recent performance over decorative charts.

## 5. AI architecture

```text
Tutor / Assessment use case
        -> AI Orchestrator
        -> AIProvider interface
        -> OpenAIProvider (MVP)
```

The provider interface exposes operations such as `generate_tutor_turn()` and `generate_questions()` and accepts typed request objects. It returns typed, schema-validated responses.

Tutor turns use explicit stages: `hook`, `explain`, `worked_example`, `interactive_question`, `hint`, `mini_challenge`, `summary`, and `mastery_check`. The UI renders a stage deliberately rather than treating every response as a free-form chat message.

Question generation produces a draft question only. The backend validates its shape, stores provenance as `AI_GENERATED`, scores attempts from its stored answer key, and never lets an LLM decide a submitted answer's score. Official PYQs are imported and labelled separately.

For the MVP, use one provider and feature flags for AI features. Provider fallback should be designed as an interface, but not implemented until a real reliability or cost requirement exists.

## 6. Database ER design

```text
users 1--1 profiles
users 1--* student_mastery *--1 curriculum_nodes
exam 1--* curriculum_versions 1--* subjects 1--* topics 1--* subtopics
curriculum_nodes *--* curriculum_nodes (prerequisites)
topics/subtopics 1--* learning_objectives
users 1--* learning_paths 1--* lessons 1--* lesson_progress
questions *--1 curriculum_nodes
quizzes 1--* quiz_questions *--1 questions
users 1--* quiz_attempts 1--* question_attempts *--1 questions
question_attempts 1--0..1 mistakes
users 1--* xp_transactions; users *--* badges via user_badges
users 1--1 streaks; users 1--* analytics_events; users 1--* ai_conversations
users 1--* assigned_topics *--1 curriculum_nodes
```

Core modelling decisions:

* Use a generic `curriculum_node` identity internally or explicit foreign-key columns with a `node_type`; choose one before Phase 2. The recommended choice is a generic node table plus child detail tables because prerequisites, mastery, questions, and assignment all need to target several hierarchy levels.
* `student_mastery` is unique on `(user_id, curriculum_node_id)` and records current estimate, confidence, evidence counts, last assessed/studied timestamps, and current difficulty.
* Preserve immutable attempt records. Derived summaries (dashboard counts, subject mastery) can be recomputed from attempts and mastery.
* Add `created_at`, `updated_at`, foreign keys, uniqueness constraints, and indexes for user-scoped timeline queries.
* Store question provenance: `OFFICIAL_SYLLABUS`, `OFFICIAL_PYQ`, `AI_GENERATED`, or `CURATED_PRACTICE`; only the latter two may come from AI.

## 7. Student knowledge model and adaptive algorithm

Each mastery record contains a score from 0–100, confidence (low/medium/high or numeric evidence weight), attempts, accuracy, median response time, misconception tags, last interaction, revision due date, and difficulty band.

Initial diagnostic scoring uses topic-tagged questions across a small set of high-value prerequisites. Each answer applies a bounded update to the related subtopic. Low-evidence scores remain low-confidence so the product does not over-personalize after one answer.

After a scored question:

1. Validate and store the attempt with response time and answer outcome.
2. Detect misconception tags using the question's known concept tags; AI may suggest tags for review, but does not alter scoring.
3. Update subtopic mastery with recency-weighted evidence, correctness, question difficulty, and response-time signal.
4. Roll up topic and subject mastery from child mastery weighted by objective importance and evidence confidence.
5. Recalculate revision due date and current difficulty.
6. Rank next actions: overdue revision, prerequisite repair, assigned topic, learning-path next node, then new weak areas.

A transparent first-version formula is preferable to Bayesian Knowledge Tracing initially:

```text
evidence = 0.75 * correctness + 0.15 * time_quality + 0.10 * difficulty_fit
new_mastery = clamp(old_mastery * (1 - learning_rate) + 100 * evidence * learning_rate)
learning_rate decreases as evidence count rises
```

Use thresholds cautiously: below 45 requires remediation; 45–74 continues guided practice; 75+ qualifies for advancement when prerequisite confidence is adequate. These thresholds are configuration, not hard-coded UI logic. Later, validate and replace the model with calibrated IRT/BKT only after enough genuine learner data exists.

## 8. API design (MVP)

All non-auth endpoints require a bearer JWT and scope records to the authenticated user.

* `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`
* `GET/PATCH /me/profile`; `POST /onboarding/complete`
* `GET /curriculum/versions`, `GET /curriculum/subjects`, `GET /curriculum/nodes/{id}`
* `POST /diagnostics/start`, `POST /diagnostics/{id}/answers`, `POST /diagnostics/{id}/complete`
* `POST /tutor/sessions`, `POST /tutor/sessions/{id}/messages`
* `POST /quizzes`, `POST /quiz-attempts/{id}/answers`, `POST /quiz-attempts/{id}/submit`
* `POST /assigned-topics`; `GET /learning-path`; `GET /recommendations`
* `GET /progress`, `GET /analytics/overview`, `GET /badges`, `GET /dashboard`

Use resource-oriented URLs, version the API under `/api/v1`, return stable error envelopes, paginate list endpoints, and represent IDs as UUIDs.

## 9. Folder structure

```text
frontend/
  app/ components/ features/ lib/ types/
backend/
  app/
    api/ core/ db/ models/ schemas/ repositories/
    services/ domain/ agents/ providers/ tests/
  alembic/
docs/
docker/
```

Feature modules may be introduced under `backend/app/services` as the product grows; avoid splitting into microservices or creating a generic `utils` dumping ground.

## 10. Authentication and security strategy

* Store passwords with Argon2id (or bcrypt if platform support forces it); never encrypt passwords reversibly.
* Use short-lived signed access JWTs and rotating refresh tokens stored/invalidated server-side. Prefer httpOnly secure cookies for browser refresh tokens; mitigate CSRF when cookies are used.
* Derive user identity only from the verified token. Every repository query involving learner data filters by that identity.
* Apply Pydantic validation, strict CORS allow-lists, rate limits for login and costly AI endpoints, request size limits, and generic public error messages.
* Keep secrets in environment configuration and commit an `.env.example`, never a real `.env` or provider key.
* Record security-relevant events without storing credentials, prompts containing sensitive data, or raw refresh tokens.

## 11. Testing strategy

* **Unit tests:** mastery update, score validation, XP, badge eligibility, recommendation ranking, prerequisite checks.
* **Repository/integration tests:** migrations, constraints, user isolation, curriculum retrieval, transactional quiz submission.
* **API tests:** registration/login, authorization, validation errors, protected-resource isolation.
* **Frontend tests:** key UI states and learning/quiz interactions.
* **End-to-end tests:** onboarding to diagnostic to recommendation; lesson to quiz to mastery update.
* **AI contract tests:** provider output validates against schemas; mock providers cover retries and malformed responses. Curated evaluation fixtures assess teaching and question quality separately from API availability.

Use a dedicated test database and run migrations in CI; do not treat a running development server as proof of correctness.

## 12. Deployment and operations

Development uses Docker Compose for PostgreSQL and optionally the app services. Production deploys the frontend and API as separate containers/services with managed PostgreSQL, TLS, environment-managed secrets, database migrations as a release step, structured logs, error tracking, health checks, and scheduled backups with restore testing.

Start with one region and one API replica. Scale only after measuring latency and load. AI calls need timeouts, retry policies for transient errors, spend caps, and graceful UI fallbacks.

## 13. MVP scope

The MVP should prove one adaptive loop, not the entire GATE product:

1. Account, onboarding, and a short diagnostic.
2. Curated versioned curriculum for two subjects (recommended: Programming & Data Structures and Algorithms) at topic/subtopic level.
3. Knowledge profile, prerequisite checks, and next-topic recommendations.
4. Structured tutor session for one topic and deterministic mini-quiz scoring.
5. Dashboard showing progress, weak areas, and the next action.
6. Basic XP/streak only if it does not delay the adaptive loop.

## 14. Future features

Full syllabus coverage, official PYQ ingestion with rights/source verification, spaced-repetition scheduling, multiple AI providers, educator/admin tooling, peer study, native apps, multilingual content, a calibrated knowledge-tracing model, and a background job system are later phases.

## 15. Risks and technical tradeoffs

* **AI accuracy:** generated explanations/questions can be wrong. Mitigate with schema validation, curated templates, provenance, review workflow, and feedback reporting.
* **Mastery validity:** a percentage can create false confidence. Track evidence confidence and treat the initial model as an evolving heuristic.
* **Official content:** do not scrape or label material official without source/rights review. Seed the first curriculum from verified official sources during Phase 2.
* **Cost and latency:** real-time AI can be slow and expensive. Keep contexts compact, cache safe reusable content, cap generation, and make rule-based recommendations first-class.
* **Overbuilding:** multi-provider support, every question type, mock exams, and advanced analytics are not MVP requirements. Interfaces now, implementations when justified.
* **Privacy:** learning data is personal. Design for deletion/export, minimal retention, and strict tenant isolation before collecting substantial user data.

## 16. Requirements to adjust

* Do not expect the diagnostic to estimate true ability precisely from a short quiz; it should produce a provisional profile that improves with evidence.
* Do not make an LLM the source of truth for mastery, syllabus, answer scoring, XP, or badges. It can assist content generation and explanations only.
* Building all GATE subjects before user testing is high-risk. Launch with two coherent subjects and expand from measured demand.
* A generic "learning style" questionnaire should not drive strong personalization; evidence from actual performance should outweigh self-report.
* A separate microservice per agent would slow development and complicate data consistency. The modular monolith is the correct initial architecture.
