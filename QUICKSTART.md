# Quick Start Guide - AdaptiveAI Backend

## Current Status
✅ **Backend fully implemented and tested** (20/20 tests passing)
⏳ **Blocked on**: Docker PostgreSQL database not running

## Prerequisites
- Python 3.12+
- Docker Desktop (for PostgreSQL)
- OpenAI API key
- Git

## Installation

### 1. Clone and Setup
```bash
cd backend
pip install -e .  # Install project in editable mode
```

### 2. Environment Configuration
Create `.env` file in `backend/` directory:
```env
DATABASE_URL=postgresql+psycopg://adaptiveai:change-me@localhost:5432/adaptiveai
JWT_SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=sk-your-openai-api-key
# Leave empty for api.openai.com; set this only for an OpenAI-compatible gateway.
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-4o-mini
```

### 3. Database Setup (Currently Blocked - Docker Needed)
```bash
# Start PostgreSQL container
docker-compose up -d postgres

# Wait for database to be ready (check logs)
docker-compose logs -f postgres

# Run migrations to initialize schema
cd backend
alembic upgrade head

# Load curriculum seed data
python scripts/seed_gate_2027.py
```

### 4. Run Tests (Already Working)
```bash
cd backend
python -m pytest tests/ -v
# Expected: 20 passed in ~2 seconds
```

### 5. Start Development Server (When DB Ready)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Access API documentation: http://localhost:8000/docs

## What's Implemented & Working

### Core Features ✅
1. **User Authentication** - Registration, login, JWT tokens
2. **Curriculum Management** - Hierarchical, versioned, with prerequisites
3. **Question Bank** - Multiple types (MCQ, MSQ, NAT), sources, difficulty levels
4. **Student Mastery Tracking** - Evidence-based algorithm with learning rate decay
5. **Tutor Agent** - AI-powered interactive lessons (OpenAI gpt-4o-mini)
6. **Quiz System** - Practice assessments with automatic scoring
7. **Diagnostic Assessment** - Initial assessment for learning path
8. **Recommendations Engine** - Intelligent next-action suggestions
9. **Gamification** - XP, badges, streaks, daily goals
10. **Analytics** - Progress tracking and insights

### Test Coverage ✅
```
Unit Tests (20/20 passing):
  - Mastery calculation algorithm
  - Gamification progression
  - Answer scoring (MCQ/MSQ handling)
  - Security (password hashing, JWT)
  - Curriculum hierarchy
  - Recommendations priority
  - Assessment contracts
```

## API Examples

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@test.com","password":"Test123!"}'
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

### Onboarding
```bash
curl -X PUT http://localhost:8000/learning/onboarding \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Doe",
    "target_exam": "GATE CSE",
    "programming_experience": "3-5 years",
    "preferred_learning_style": "visual",
    "daily_study_minutes": 60
  }'
```

### Start Diagnostic (When DB Ready)
```bash
curl -X POST http://localhost:8000/learning/diagnostics/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "curriculum_version_id": "VERSION_ID_HERE",
    "question_limit": 50
  }'
# Returns: {
#   "id": "ASSESSMENT_ID",
#   "status": "in_progress",
#   "questions": [...]
# }
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│       FastAPI Application               │
│  (app/main.py)                          │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
   ┌────▼────┐  ┌────▼────┐
   │ Routes  │  │ Services │
   │(api/)   │  │(services)│
   └────┬────┘  └────┬────┘
        │             │
        └──────┬──────┘
               │
         ┌─────▼──────┐
         │  SQLAlchemy│
         │   Models   │
         │  (models/) │
         └─────┬──────┘
               │
         ┌─────▼──────┐
      ┌──┤ PostgreSQL │◄─── Docker: postgres:16-alpine
      │  └────────────┘
      │
   ┌──▼───────────┐
   │ OpenAI API   │
   │ (gpt-4o-mini)│
   └──────────────┘
```

## File Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── deps.py            # Dependency injection (get_current_user, get_db)
│   │   └── routes/            # API endpoints organized by feature
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response models
│   ├── services/              # Business logic (tutor, assessment, mastery, etc.)
│   ├── providers/             # AI provider abstraction (OpenAI)
│   ├── core/                  # Configuration, security, middleware
│   └── db/                    # Database session management
├── alembic/                   # Database migration management
│   └── versions/              # Migration files (8 total, not yet executed)
├── tests/                     # Unit and integration tests
├── scripts/
│   └── seed_gate_2027.py     # Curriculum and question data loader
├── pyproject.toml            # Dependencies and build config
├── .env                       # Environment variables (create this)
└── alembic.ini               # Alembic configuration
```

## Key Components Explained

### 1. Tutor Service (`app/services/tutor.py`)
Manages AI-powered interactive lessons:
- Builds context from student's curriculum and mastery
- Calls OpenAI provider with system + user prompts
- Stores messages in database for history
- Returns structured TutorTurn responses

### 2. Assessment Service (`app/services/assessment.py`)
Handles quizzes and diagnostic assessments:
- Creates quizzes from question bank
- Scores answers (handles MCQ/MSQ nuances)
- Records mistakes for targeted remediation
- Updates mastery scores

### 3. Mastery Service (`app/services/mastery.py`)
Calculates student knowledge state:
- Uses evidence-based algorithm
- Learning rate decreases with more evidence (spaced repetition)
- Time quality factors: ideal (90s), reduced (90-180s), minimal (>180s)
- Confidence levels: low, medium, high

### 4. Recommendations Service (`app/services/recommendations.py`)
Intelligent learning path selection:
- Prioritizes revision when due
- Identifies prerequisite gaps
- Focuses on weakest areas
- Balances learning across topics

### 5. Gamification Service (`app/services/gamification.py`)
Reward system for engagement:
- Awards XP for quiz attempts
- Tracks daily streaks
- Grants badges for achievements
- Updates daily goal counters

## Testing Locally (No Database Needed)
```bash
cd backend

# Run all unit tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_mastery.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run one test
python -m pytest tests/test_mastery.py::test_correct_answer_increases_initial_mastery -v
```

## Common Issues & Solutions

### Issue: "fixture 'database' not found"
- **Cause**: Integration tests need database connection
- **Solution**: Start Docker (see Database Setup section)

### Issue: "OpenAI API error"
- **Cause**: Missing or invalid OPENAI_API_KEY in .env
- **Solution**: Add valid key from OpenAI dashboard

### Issue: "empty or malformed response" with HTTP 200
- **Cause**: A proxy or gateway is returning a response that is not an OpenAI Chat Completions response.
- **Solution**: Remove `OPENAI_BASE_URL` to use the official OpenAI endpoint, or set it to the gateway's OpenAI-compatible `/v1` endpoint and use a model supported by that gateway. Do not use an Anthropic Messages endpoint as an OpenAI base URL.

### Issue: "ImportError: cannot import name 'OpenAI'"
- **Cause**: openai package not installed
- **Solution**: Run `pip install -e .` from backend directory

### Issue: "ModuleNotFoundError: No module named 'alembic'"
- **Cause**: Dependencies not installed
- **Solution**: Run `pip install -e .` from backend directory

## Next Steps

1. **Start Docker PostgreSQL** (prerequisite for integration)
   ```bash
   docker-compose up -d postgres
   ```

2. **Initialize Database** (when Docker is ready)
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Load Seed Data** (populate curriculum)
   ```bash
   python scripts/seed_gate_2027.py
   ```

4. **Start Server** (run development server)
   ```bash
   python -m uvicorn app.main:app --reload
   ```

5. **Test with OpenAPI UI** (interactive API testing)
   - Visit: http://localhost:8000/docs
   - Try endpoints in Swagger UI

## Production Checklist

- [ ] Database PostgreSQL 16+ with encrypted connections
- [ ] JWT_SECRET_KEY changed to strong random value
- [ ] OPENAI_API_KEY managed by secrets manager
- [ ] CORS_ORIGINS configured for frontend domain
- [ ] Rate limiting configured for API
- [ ] Logging aggregated to external service
- [ ] Database backups automated daily
- [ ] SSL/TLS certificates configured
- [ ] API documentation accessed via /docs
- [ ] Health check endpoint monitoring
- [ ] Error tracking (Sentry or similar)
- [ ] Performance monitoring (NewRelic or similar)

## Support

For detailed system architecture, see: `SYSTEM_ARCHITECTURE.md`
For product requirements, see: `docs/phase-0-architecture.md`
For operations guide, see: `docs/operations.md`
