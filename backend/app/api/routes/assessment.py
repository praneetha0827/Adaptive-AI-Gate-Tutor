from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assessment import CreateQuizRequest, QuizQuestionResponse, QuizResponse, QuizResultResponse, SubmitQuizRequest
from app.services.assessment import create_quiz, submit_quiz

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_practice_quiz(payload: CreateQuizRequest, current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> QuizResponse:
    quiz, attempt, questions = create_quiz(database, current_user.id, payload.subtopic_ids, payload.question_count, payload.title, payload.time_limit_seconds)
    return QuizResponse(quiz_id=quiz.id, attempt_id=attempt.id, title=quiz.title, questions=[QuizQuestionResponse(id=question.id, question_type=question.question_type, prompt=question.prompt, options=question.options, difficulty=question.difficulty) for question in questions])


@router.post("/quiz-attempts/{attempt_id}/submit", response_model=QuizResultResponse)
def submit_practice_quiz(attempt_id: str, payload: SubmitQuizRequest, current_user: Annotated[User, Depends(get_current_user)], database: Annotated[Session, Depends(get_db)]) -> QuizResultResponse:
    attempt, mistakes_created, reviews = submit_quiz(database, current_user.id, attempt_id, [(answer.question_id, answer.answer, answer.response_time_ms) for answer in payload.answers])
    return QuizResultResponse(score_percent=attempt.score_percent or 0, correct_count=round((attempt.score_percent or 0) * len(payload.answers) / 100), question_count=len(payload.answers), mistakes_created=mistakes_created, reviews=reviews)
