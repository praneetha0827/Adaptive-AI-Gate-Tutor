# AdaptiveAI System Architecture & Implementation Guide

## Overview
AdaptiveAI is a production-quality, AI-powered adaptive learning platform for GATE exam preparation. The system uses OpenAI's LLM capabilities combined with spaced repetition and mastery-based learning algorithms to deliver personalized educational experiences.

## System Architecture

### Core Components

#### 1. User & Authentication System
- **Model**: `User` (email, password_hash, created_at)
- **Profile**: `Profile` (display_name, target_exam, preferred_learning_style, daily_study_minutes)
- **Auth Flow**: 
  - Registration → password hashing (Argon2, OWASP-compliant)
  - Login → JWT token generation (HS256, 30-min expiry)
  - All protected endpoints require valid JWT + current user

#### 2. Curriculum Structure (Hierarchical & Versioned)
```
Exam (GATE CSE, GATE ECE, etc.)
  └─ CurriculumVersion (2027, 2028, etc.) [status: draft/published/retired]
      └─ Subject (Data Structures, Algorithms, etc.)
          └─ Topic (Sorting, Searching, etc.)
              └─ Subtopic (Quick Sort, Merge Sort, etc.)
                  └─ LearningObjective (understand algorithm, analyze complexity, etc.)
```

**Key Features**:
- Versioning allows multiple exam years without duplicate data
- Prerequisite relationships between subtopics (captured in `Prerequisite` table)
- Display ordering for curriculum traversal
- Supports multiple subjects per version

#### 3. Question Bank & Assessment
- **Question Types**: MCQ (single correct), MSQ (multiple correct), NAT (numeric answer)
- **Question Sources**: curated_practice, ai_generated, official_pyq
- **Question Fields**:
  - `prompt`: The actual question text
  - `correct_answer`: Expected answer(s)
  - `options`: JSON array of {label, text} pairs for MCQ/MSQ
  - `concept`: Learning concept tested (e.g., "QuickSort Complexity")
  - `difficulty`: 1-5 scale for adaptive selection
  - `is_diagnostic_eligible`: Flag for questions used in initial assessment
  - `is_active`: Soft-delete mechanism

**Assessment Workflow**:
1. **Diagnostic Assessment** - Initial full assessment on all subtopics (50-100 questions)
   - Creates `DiagnosticAssessment` record
   - Creates `DiagnosticAttempt` for each question
   - Records answers with response times
   - Initializes `StudentMastery` records based on performance

2. **Practice Quizzes** - Targeted practice on specific subtopics
   - Creates `Quiz` record with title and time limit
   - Creates `QuizQuestion` for each question in quiz (display_order)
   - Creates `QuizAttempt` for student's attempt
   - Tracks individual `QuestionAttempt` records
   - Scores answers and creates `Mistake` records for incorrect answers

#### 4. Student Mastery Tracking
**StudentMastery Model**:
```python
mastery_score: float (0-100)           # Normalized probability student knows concept
evidence_count: int                     # Number of times assessed (higher = more confident)
correct_count: int                      # Cumulative correct answers
average_response_time_ms: int           # Average time to answer
last_assessed_at: datetime             # When last assessed
revision_due_at: datetime              # When concept needs revision (spaced repetition)
```

**Mastery Calculation Algorithm**:
```python
time_quality = 1.0 if response_time <= 90s else 0.7 if <= 180s else 0.4
evidence = 0.85 + 0.15 * time_quality if correct else 0.0
learning_rate = max(0.08, 0.35 / (1 + evidence_count * 0.15))
new_score = current * (1 - learning_rate) + 100 * evidence * learning_rate
```

**Properties**:
- Correct fast answers improve mastery more than correct slow answers
- Incorrect answers decrease mastery but not to zero
- Learning rate decreases with more evidence (fewer large updates)
- Confidence levels: low (0-4), medium (5-11), high (12+)

#### 5. AI-Powered Tutor Service
**Architecture**:
```
User Request → TutorContext Builder → OpenAI Provider → TutorTurn Response
```

**TutorContext** (built dynamically):
- Topic and subtopic titles
- Subtopic description and learning objectives
- Student's current mastery score for this subtopic
- Evidence count (confidence level)
- Student's previous mistakes on this topic
- Prerequisite knowledge status

**OpenAI Integration**:
- Model: `gpt-4o-mini` (cost-effective, high quality)
- Features: Structured output with Pydantic validation
- Temperature: 0.7 (balanced between creative and consistent)
- Max tokens: 1000 per response
- Error handling: Custom `AIProviderError` with retry logic

**TutorTurn Response** (validated schema):
```python
stage: "hook" | "explain" | "worked_example" | "interactive_question" | "hint" | "mini_challenge" | "summary" | "mastery_check"
explanation: str (1-4000 chars)          # Main content
question: str | None (1-1500 chars)      # If stage requires question
hint: str | None (1-1500 chars)          # If student asks or needed
difficulty: int (1-5)                     # Adaptive difficulty level
```

**Session Management**:
- Creates `TutorSession` record with context snapshot
- Stores conversation history in `TutorMessage` records
- Preserves context across multi-turn conversations
- Supports session closure and history retrieval

#### 6. Recommendations Engine
**Intelligent Routing** (`get_next_action()`):

Priority order:
1. **No history?** → Recommend diagnostic assessment
2. **Revision due?** → Prioritize revision (spaced repetition)
3. **Prerequisite weak?** → Recommend remediation
4. **Weak topics?** → Focus on lowest mastery
5. **Need evidence?** → Revisit topics with low evidence count
6. **Ready for new?** → Balance learning across all topics

**NextAction Response**:
```python
action: "diagnostic" | "revision" | "remediation" | "learn"
subtopic_id: str | None                  # Recommended subtopic
subtopic_title: str | None
reason: str                               # Explanation for student
mastery_score: float | None               # Current performance
confidence: "low" | "medium" | "high"    # Evidence-based confidence
```

#### 7. Gamification System
**Reward Mechanisms**:

**XP (Experience Points)**:
- Base: 5 XP per quiz
- Per correct answer: +10 XP
- Level = total_xp // 100 + 1

**Streaks**:
- Daily activity tracking
- Longest streak record
- Current day counter
- Last activity date

**Daily Goals**:
- Track questions answered today
- Cumulative across all quizzes
- Timezone-aware UTC

**Badges** (Achievement system):
- `first_quiz`: Complete 1st quiz
- `hundred_questions`: Answer 100 questions total
- `perfect_quiz`: Score 100% on any quiz
- `seven_day_streak`: Maintain 7-day learning streak

#### 8. Analytics & Progress Tracking
**Analytics Overview** includes:
```python
questions_attempted: int               # Total questions answered
accuracy_percent: float                # Overall correct %
average_response_time_seconds: float  # Avg time per question
learning_time_minutes: int             # Total time invested
subject_mastery: list[{id, title, mastery_score}]  # By subject
weak_topics: list[{id, title, mastery_score}]      # Bottom 5
strong_topics: list[{id, title, mastery_score}]    # Top 5
recent_quiz_scores: list[{quiz_id, score_percent, submitted_at}]
```

## API Routes

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `POST /auth/me` - Get current user info

### Onboarding
- `PUT /learning/onboarding` - Store preferences and profile

### Diagnostic Assessment
- `POST /learning/diagnostics/start` - Begin diagnostic (returns questions)
- `POST /learning/diagnostics/{assessment_id}/submit` - Submit answers (scores and initializes mastery)
- `GET /learning/progress/mastery` - View current mastery scores

### Tutor (Interactive Learning)
- `POST /tutor/sessions` - Start lesson on specific subtopic
- `POST /tutor/sessions/{session_id}/messages` - Continue conversation
- `POST /tutor/recommended-session` - Start lesson based on recommendation

### Assessment (Practice Quizzes)
- `POST /assessment/quizzes` - Create quiz from subtopics
- `POST /assessment/quiz-attempts/{attempt_id}/submit` - Submit quiz answers

### Analytics
- Not yet exposed in routes, but available for dashboard

## Database Schema

### Core Tables
- `users` - User accounts
- `profiles` - User preferences
- `exams` - GATE exams
- `curriculum_versions` - Curriculum versions (2027, 2028, etc.)
- `subjects` - Subject areas
- `topics` - Topics within subjects
- `subtopics` - Subtopics within topics
- `learning_objectives` - Learning goals
- `prerequisites` - Topic prerequisites

### Question Tables
- `questions` - All questions
- `question_sources` - Source types (curated, AI-generated, etc.)

### Assessment Tables
- `diagnostic_assessments` - Diagnostic test records
- `diagnostic_attempts` - Individual diagnostic question attempts
- `quizzes` - Practice quiz definitions
- `quiz_questions` - Questions in each quiz
- `quiz_attempts` - Student's quiz attempts
- `question_attempts` - Individual question answers in a quiz

### Learning Tables
- `student_mastery` - Knowledge tracking per student per subtopic
- `mistakes` - Failed attempts for targeted remediation

### Interaction Tables
- `tutor_sessions` - Tutor conversation sessions
- `tutor_messages` - Individual messages in sessions

### Gamification Tables
- `xp_transactions` - XP rewards
- `streaks` - Daily streak tracking
- `daily_goals` - Daily learning goals
- `badges` - Badge definitions
- `user_badges` - Earned badges

### Analytics Tables
- `analytics_events` - User action events

## Data Flow Examples

### Example 1: Diagnostic Assessment → Mastery Initialization
```
1. User completes onboarding
2. GET /learning/diagnostics/start
   - Loads 50 diagnostic-eligible questions
   - Creates DiagnosticAssessment (status=in_progress)
   - Returns questions to client
3. User answers 50 questions
4. POST /learning/diagnostics/{id}/submit with 50 answers
   - Scores each answer
   - For each correct answer: record_diagnostic_evidence(user, subtopic, True, response_time)
     - Creates or updates StudentMastery
     - Sets mastery_score based on algorithm
     - Sets evidence_count = 1
     - Sets revision_due_at based on confidence
   - Creates Mistake records for incorrect answers
   - Marks assessment as completed
5. GET /learning/progress/mastery
   - Returns all StudentMastery records with confidence levels
```

### Example 2: Adaptive Tutor Session → Quiz → Rewards
```
1. POST /tutor/recommended-session
   - get_next_action() determines what to study
   - create_session() called with recommended subtopic
     - build_tutor_context() fetches curriculum + mastery
     - provider.generate_tutor_turn() calls OpenAI
     - Stores TutorSession + first TutorMessage (role=assistant)
   - Returns session_id + first TutorTurn
2. User reads explanation, interacts with content
3. POST /tutor/sessions/{session_id}/messages with student answer
   - continue_session() called
   - Stores TutorMessage (role=user)
   - provider.generate_tutor_turn() with updated context
   - Stores TutorMessage (role=assistant) with turn data
   - Returns next TutorTurn
4. Loop continues until student feels ready
5. POST /assessment/quizzes to practice this topic
6. Student answers 10 questions
7. POST /assessment/quiz-attempts/{attempt_id}/submit with 10 answers
   - Scores each answer
   - Updates StudentMastery for this subtopic
   - Creates Mistake records for incorrect
   - record_quiz_rewards():
     - Adds XP transaction
     - Updates/creates Streak
     - Updates DailyGoal
     - Checks for badge eligibility
8. Returns score_percent and mistakes_created
9. User can now start new recommendation cycle
```

## Transaction Safety

All database updates are wrapped in transactions with commit/rollback:
- Diagnostic submission: Atomically records all answers + mastery updates
- Quiz submission: Atomically scores + updates mastery + records rewards
- Session creation: Atomically creates session + stores initial message
- Recommendation: Reads-only, no transactions needed

## Error Handling

### HTTP Status Codes
- `400 Bad Request` - Invalid input validation
- `401 Unauthorized` - Missing or invalid JWT
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - State violation (already submitted, etc.)
- `422 Unprocessable Entity` - Invalid data format
- `503 Service Unavailable` - AI provider error

### Custom Exceptions
- `LookupError` → 404 Not Found (missing subtopic, session, etc.)
- `AIProviderError` → 503 Service Unavailable (OpenAI API errors)
- `HTTPException` → Returned by services with specific status codes

## Testing Strategy

### Unit Tests (20 currently passing)
- Mastery calculation algorithm
- Gamification level progression
- Answer scoring (MCQ vs MSQ)
- Curriculum model validation
- Security (password hashing, JWT)
- Recommendation priority logic
- Assessment contract validation

### Integration Tests (ready when DB available)
- End-to-end diagnostic workflow
- Mastery update after quiz
- Recommendation accuracy
- Tutor context building
- Analytics aggregation

### Manual Testing (when Docker running)
1. Start database: `docker-compose up -d postgres`
2. Run migrations: `alembic upgrade head`
3. Load seed data: `python scripts/seed_gate_2027.py`
4. Start server: `python -m uvicorn app.main:app --reload`
5. Test endpoints via OpenAPI: http://localhost:8000/docs

## Deployment Readiness

✅ **Production-Ready Components**:
- Authentication & authorization
- Database schema & migrations
- Service layer architecture
- Error handling & validation
- Pydantic serialization
- OpenAI integration
- Mastery algorithm
- Gamification system
- Analytics tracking

⏳ **Still Needed**:
- Database initialization (Docker + PostgreSQL)
- Curriculum seed data loading
- Question bank population
- Frontend development
- Load testing
- Security audit
- Performance optimization

## Future Enhancements

1. **AI Question Generation**: Use OpenAI to generate new questions on demand
2. **Adaptive Difficulty**: Adjust quiz difficulty based on real-time performance
3. **Collaborative Learning**: Study groups, peer discussion forums
4. **Mobile App**: Native iOS/Android for on-the-go learning
5. **Video Content**: Integrate YouTube, Khan Academy tutorials
6. **Mock Exams**: Full-length timed exams with detailed analytics
7. **Instructor Dashboard**: Monitor student progress, generate reports
8. **Social Features**: Leaderboards, achievement sharing
