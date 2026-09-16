from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.learning import StudentMastery


def calculate_updated_mastery(current_score: float, evidence_count: int, is_correct: bool, response_time_ms: int) -> float:
    time_quality = 1.0 if response_time_ms <= 90_000 else 0.7 if response_time_ms <= 180_000 else 0.4
    evidence = (0.85 + 0.15 * time_quality) if is_correct else 0.0
    learning_rate = max(0.08, 0.35 / (1 + evidence_count * 0.15))
    return round(max(0.0, min(100.0, current_score * (1 - learning_rate) + 100 * evidence * learning_rate)), 2)


def record_diagnostic_evidence(database: Session, user_id: str, subtopic_id: str, is_correct: bool, response_time_ms: int) -> StudentMastery:
    mastery = database.query(StudentMastery).filter_by(user_id=user_id, subtopic_id=subtopic_id).one_or_none()
    now = datetime.now(UTC)
    if mastery is None:
        mastery = StudentMastery(user_id=user_id, subtopic_id=subtopic_id, mastery_score=50.0, evidence_count=0, correct_count=0)
        database.add(mastery)
    prior_count = mastery.evidence_count
    mastery.mastery_score = calculate_updated_mastery(mastery.mastery_score, prior_count, is_correct, response_time_ms)
    mastery.evidence_count = prior_count + 1
    mastery.correct_count += int(is_correct)
    mastery.average_response_time_ms = response_time_ms if mastery.average_response_time_ms is None else round((mastery.average_response_time_ms * prior_count + response_time_ms) / mastery.evidence_count)
    mastery.last_assessed_at = now
    mastery.revision_due_at = now + timedelta(days=2 if mastery.mastery_score < 45 else 7 if mastery.mastery_score < 75 else 21)
    return mastery


def mastery_confidence(evidence_count: int) -> str:
    return "high" if evidence_count >= 12 else "medium" if evidence_count >= 5 else "low"
