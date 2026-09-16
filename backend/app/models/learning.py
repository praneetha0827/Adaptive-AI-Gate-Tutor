from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuestionSource(StrEnum):
    CURATED_PRACTICE = "curated_practice"
    AI_GENERATED = "ai_generated"
    OFFICIAL_PYQ = "official_pyq"


class QuestionType(StrEnum):
    MCQ = "mcq"
    MSQ = "msq"
    NAT = "nat"


class DiagnosticStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (CheckConstraint("difficulty BETWEEN 1 AND 5", name="ck_question_difficulty"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="RESTRICT"), index=True)
    source: Mapped[QuestionSource] = mapped_column(String(30))
    question_type: Mapped[QuestionType] = mapped_column(String(10))
    prompt: Mapped[str] = mapped_column(Text)
    options: Mapped[list[dict[str, str]] | None] = mapped_column(JSON)
    correct_answer: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    concept: Mapped[str] = mapped_column(String(150))
    skill_tested: Mapped[str] = mapped_column(String(150))
    difficulty: Mapped[int] = mapped_column(Integer)
    is_diagnostic_eligible: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DiagnosticAssessment(Base):
    __tablename__ = "diagnostic_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    curriculum_version_id: Mapped[str] = mapped_column(ForeignKey("curriculum_versions.id", ondelete="RESTRICT"), index=True)
    status: Mapped[DiagnosticStatus] = mapped_column(String(20), default=DiagnosticStatus.IN_PROGRESS)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DiagnosticAttempt(Base):
    __tablename__ = "diagnostic_attempts"
    __table_args__ = (UniqueConstraint("diagnostic_assessment_id", "question_id", name="uq_diagnostic_question"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    diagnostic_assessment_id: Mapped[str] = mapped_column(ForeignKey("diagnostic_assessments.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    submitted_answer: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StudentMastery(Base):
    __tablename__ = "student_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "subtopic_id", name="uq_student_mastery_user_subtopic"),
        CheckConstraint("mastery_score BETWEEN 0 AND 100", name="ck_student_mastery_score"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="CASCADE"), index=True)
    mastery_score: Mapped[float] = mapped_column(Float, default=50.0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    average_response_time_ms: Mapped[int | None] = mapped_column(Integer)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revision_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(150))
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (UniqueConstraint("quiz_id", "question_id", name="uq_quiz_question"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    display_order: Mapped[int] = mapped_column(Integer)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score_percent: Mapped[float | None] = mapped_column(Float)


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"
    __table_args__ = (UniqueConstraint("quiz_attempt_id", "question_id", name="uq_quiz_attempt_question"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    quiz_attempt_id: Mapped[str] = mapped_column(ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"), index=True)
    submitted_answer: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    question_attempt_id: Mapped[str] = mapped_column(ForeignKey("question_attempts.id", ondelete="CASCADE"), unique=True, index=True)
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="RESTRICT"), index=True)
    concept: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
