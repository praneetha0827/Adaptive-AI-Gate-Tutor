from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import Subtopic, Subject, Topic
from app.models.learning import DiagnosticAssessment, DiagnosticAttempt, DiagnosticStatus, Question
from app.services.assessment import is_correct_answer
from app.services.mastery import record_diagnostic_evidence


def start_diagnostic(database: Session, user_id: str, curriculum_version_id: str, question_limit: int) -> tuple[DiagnosticAssessment, list[Question]]:
    questions = list(database.scalars(
        select(Question)
        .join(Subtopic, Question.subtopic_id == Subtopic.id)
        .join(Topic, Subtopic.topic_id == Topic.id)
        .join(Subject, Topic.subject_id == Subject.id)
        .where(Subject.curriculum_version_id == curriculum_version_id, Question.is_active, Question.is_diagnostic_eligible)
        .limit(question_limit)
    ))
    if len(questions) < 5:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Diagnostic question bank is not ready for this curriculum version")
    assessment = DiagnosticAssessment(user_id=user_id, curriculum_version_id=curriculum_version_id)
    database.add(assessment)
    database.flush()
    database.add_all(DiagnosticAttempt(diagnostic_assessment_id=assessment.id, question_id=question.id) for question in questions)
    database.commit()
    database.refresh(assessment)
    return assessment, questions


def submit_diagnostic(database: Session, user_id: str, assessment_id: str, answers: list[tuple[str, str, int]]) -> DiagnosticAssessment:
    assessment = database.get(DiagnosticAssessment, assessment_id)
    if assessment is None or assessment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic assessment not found")
    if assessment.status == DiagnosticStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Diagnostic assessment is already complete")
    attempts = list(database.scalars(select(DiagnosticAttempt).where(DiagnosticAttempt.diagnostic_assessment_id == assessment.id)))
    attempts_by_question = {attempt.question_id: attempt for attempt in attempts}
    questions = {question.id: question for question in database.scalars(select(Question).where(Question.id.in_(attempts_by_question)))}
    if set(question_id for question_id, _, _ in answers) != set(attempts_by_question):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Submit one answer for every diagnostic question")
    for question_id, answer, response_time_ms in answers:
        attempt = attempts_by_question[question_id]
        question = questions[question_id]
        is_correct = is_correct_answer(question, answer)
        attempt.submitted_answer = answer
        attempt.response_time_ms = response_time_ms
        attempt.is_correct = is_correct
        attempt.answered_at = datetime.now(UTC)
        record_diagnostic_evidence(database, user_id, question.subtopic_id, is_correct, response_time_ms)
    assessment.status = DiagnosticStatus.COMPLETED
    assessment.completed_at = datetime.now(UTC)
    database.commit()
    database.refresh(assessment)
    return assessment
