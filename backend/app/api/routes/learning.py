from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.learning import StudentMastery
from app.models.user import Profile, User
from app.schemas.learning import (
    DiagnosticAssessmentResponse,
    DiagnosticQuestionResponse,
    MasteryResponse,
    OnboardingRequest,
    StartDiagnosticRequest,
    SubmitDiagnosticRequest,
)
from app.services.diagnostics import start_diagnostic, submit_diagnostic
from app.services.mastery import mastery_confidence

router = APIRouter(tags=["learning"])


@router.put("/onboarding", status_code=status.HTTP_204_NO_CONTENT)
def complete_onboarding(
    payload: OnboardingRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
) -> None:
    profile = database.scalar(select(Profile).where(Profile.user_id == current_user.id))
    if profile is None:
        profile = Profile(user_id=current_user.id)
        database.add(profile)
    profile.display_name = payload.display_name
    profile.target_exam = payload.target_exam
    profile.target_year = payload.target_year
    profile.target_rank = payload.target_rank
    profile.daily_study_minutes = payload.daily_study_minutes
    profile.programming_experience = payload.programming_experience
    profile.preferred_learning_style = payload.preferred_learning_style
    profile.subject_confidence = payload.subject_confidence
    from datetime import UTC, datetime

    profile.onboarding_completed_at = datetime.now(UTC)
    database.commit()


@router.post("/diagnostics/start", response_model=DiagnosticAssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostic(
    payload: StartDiagnosticRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
) -> DiagnosticAssessmentResponse:
    assessment, questions = start_diagnostic(database, current_user.id, payload.curriculum_version_id, payload.question_limit)
    return DiagnosticAssessmentResponse(
        id=assessment.id,
        status=assessment.status,
        questions=[DiagnosticQuestionResponse(id=question.id, question_type=question.question_type, prompt=question.prompt, options=question.options) for question in questions],
    )


@router.post("/diagnostics/{assessment_id}/submit", status_code=status.HTTP_204_NO_CONTENT)
def complete_diagnostic(
    assessment_id: str,
    payload: SubmitDiagnosticRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
) -> None:
    submit_diagnostic(database, current_user.id, assessment_id, [(answer.question_id, answer.answer, answer.response_time_ms) for answer in payload.answers])


@router.get("/progress/mastery", response_model=list[MasteryResponse])
def read_mastery(
    current_user: Annotated[User, Depends(get_current_user)],
    database: Annotated[Session, Depends(get_db)],
) -> list[MasteryResponse]:
    records = database.scalars(select(StudentMastery).where(StudentMastery.user_id == current_user.id).order_by(StudentMastery.mastery_score)).all()
    return [MasteryResponse(subtopic_id=record.subtopic_id, mastery_score=record.mastery_score, evidence_count=record.evidence_count, confidence=mastery_confidence(record.evidence_count)) for record in records]
