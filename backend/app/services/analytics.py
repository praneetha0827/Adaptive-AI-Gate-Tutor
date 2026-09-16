from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import Subject, Subtopic, Topic
from app.models.learning import QuestionAttempt, QuizAttempt, StudentMastery


def analytics_overview(database: Session, user_id: str) -> dict[str, object]:
    attempts = list(database.scalars(select(QuestionAttempt).join(QuizAttempt).where(QuizAttempt.user_id == user_id, QuizAttempt.submitted_at.is_not(None))))
    questions_attempted = len(attempts)
    correct_count = sum(bool(attempt.is_correct) for attempt in attempts)
    response_times = [attempt.response_time_ms for attempt in attempts if attempt.response_time_ms is not None]
    mastery = list(database.execute(select(StudentMastery, Subtopic, Topic, Subject).join(Subtopic, StudentMastery.subtopic_id == Subtopic.id).join(Topic, Subtopic.topic_id == Topic.id).join(Subject, Topic.subject_id == Subject.id).where(StudentMastery.user_id == user_id)).all())
    subject_scores: dict[str, list[float]] = {}
    topic_scores: dict[tuple[str, str], list[float]] = {}
    for record, subtopic, topic, subject in mastery:
        subject_scores.setdefault(subject.id, [subject.title, 0.0, 0.0])
        subject_scores[subject.id][1] += record.mastery_score
        subject_scores[subject.id][2] += 1
        topic_scores.setdefault((topic.id, topic.title), []).append(record.mastery_score)
    subject_mastery = [{"id": subject_id, "title": values[0], "mastery_score": round(values[1] / values[2], 2)} for subject_id, values in subject_scores.items()]
    topic_rollups = [{"id": topic_id, "title": title, "mastery_score": round(sum(scores) / len(scores), 2)} for (topic_id, title), scores in topic_scores.items()]
    recent = list(database.scalars(select(QuizAttempt).where(QuizAttempt.user_id == user_id, QuizAttempt.submitted_at.is_not(None)).order_by(QuizAttempt.submitted_at.desc()).limit(10)))
    return {"questions_attempted": questions_attempted, "accuracy_percent": round(100 * correct_count / questions_attempted, 2) if questions_attempted else 0, "average_response_time_seconds": round(sum(response_times) / len(response_times) / 1000, 2) if response_times else 0, "learning_time_minutes": round(sum(response_times) / 60_000) if response_times else 0, "subject_mastery": sorted(subject_mastery, key=lambda item: item["title"]), "weak_topics": sorted(topic_rollups, key=lambda item: item["mastery_score"])[:5], "strong_topics": sorted(topic_rollups, key=lambda item: item["mastery_score"], reverse=True)[:5], "recent_quiz_scores": [{"quiz_id": attempt.quiz_id, "score_percent": attempt.score_percent or 0, "submitted_at": attempt.submitted_at.isoformat()} for attempt in recent]}
