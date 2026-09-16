from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning import Mistake, Question, QuestionAttempt, Quiz, QuizAttempt, QuizQuestion
from app.services.mastery import record_diagnostic_evidence
from app.services.gamification import record_quiz_rewards
from app.models.analytics import AnalyticsEvent


def is_correct_answer(question: Question, answer: str) -> bool:
    if question.question_type == "msq":
        expected = {value.strip().casefold() for value in question.correct_answer.split(",") if value.strip()}
        submitted = {value.strip().casefold() for value in answer.split(",") if value.strip()}
        return submitted == expected
    return answer.strip().casefold() == question.correct_answer.strip().casefold()


def create_quiz(database: Session, user_id: str, subtopic_ids: list[str], question_count: int, title: str, time_limit_seconds: int | None) -> tuple[Quiz, QuizAttempt, list[Question]]:
    questions = list(database.scalars(select(Question).where(Question.subtopic_id.in_(subtopic_ids), Question.is_active).order_by(Question.difficulty).limit(question_count)))
    if len(questions) < question_count:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not enough approved questions for this quiz")
    quiz = Quiz(user_id=user_id, title=title, time_limit_seconds=time_limit_seconds)
    database.add(quiz)
    database.flush()
    database.add_all(QuizQuestion(quiz_id=quiz.id, question_id=question.id, display_order=index) for index, question in enumerate(questions, start=1))
    attempt = QuizAttempt(quiz_id=quiz.id, user_id=user_id)
    database.add(attempt)
    database.commit()
    database.refresh(quiz)
    database.refresh(attempt)
    return quiz, attempt, questions


def submit_quiz(database: Session, user_id: str, attempt_id: str, answers: list[tuple[str, str, int]]) -> tuple[QuizAttempt, int, list[dict[str, str | bool]]]:
    attempt = database.get(QuizAttempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz attempt not found")
    if attempt.submitted_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Quiz attempt is already submitted")
    question_ids = set(database.scalars(select(QuizQuestion.question_id).where(QuizQuestion.quiz_id == attempt.quiz_id)))
    if {question_id for question_id, _, _ in answers} != question_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Submit one answer for every quiz question")
    questions = {question.id: question for question in database.scalars(select(Question).where(Question.id.in_(question_ids)))}
    correct_count = 0
    mistakes_created = 0
    reviews: list[dict[str, str | bool]] = []
    for question_id, answer, response_time_ms in answers:
        question = questions[question_id]
        is_correct = is_correct_answer(question, answer)
        reviews.append({"prompt": question.prompt, "submitted_answer": answer, "correct_answer": question.correct_answer, "explanation": question.explanation, "is_correct": is_correct})
        question_attempt = QuestionAttempt(quiz_attempt_id=attempt.id, question_id=question.id, submitted_answer=answer, is_correct=is_correct, response_time_ms=response_time_ms)
        database.add(question_attempt)
        database.flush()
        record_diagnostic_evidence(database, user_id, question.subtopic_id, is_correct, response_time_ms)
        if is_correct:
            correct_count += 1
        else:
            database.add(Mistake(user_id=user_id, question_attempt_id=question_attempt.id, subtopic_id=question.subtopic_id, concept=question.concept))
            mistakes_created += 1
    attempt.score_percent = round(100 * correct_count / len(question_ids), 2)
    attempt.submitted_at = datetime.now(UTC)
    record_quiz_rewards(database, user_id, attempt, correct_count, len(question_ids))
    database.add(AnalyticsEvent(user_id=user_id, event_type="quiz_completed", payload={"quiz_id": attempt.quiz_id, "score_percent": attempt.score_percent}))
    database.commit()
    database.refresh(attempt)
    return attempt, mistakes_created, reviews
