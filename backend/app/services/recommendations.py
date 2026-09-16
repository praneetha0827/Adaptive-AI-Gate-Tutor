from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import Prerequisite, Subtopic
from app.models.learning import StudentMastery
from app.services.mastery import mastery_confidence


@dataclass(frozen=True)
class NextAction:
    action: str
    subtopic_id: str | None
    subtopic_title: str | None
    reason: str
    mastery_score: float | None
    confidence: str | None


def get_next_action(database: Session, user_id: str, now: datetime | None = None) -> NextAction:
    now = now or datetime.now(UTC)
    mastery_records = list(database.scalars(select(StudentMastery).where(StudentMastery.user_id == user_id)))
    if not mastery_records:
        return NextAction("diagnostic", None, None, "Complete a diagnostic assessment so your learning path starts with evidence.", None, None)
    subtopics = {subtopic.id: subtopic for subtopic in database.scalars(select(Subtopic).where(Subtopic.id.in_([record.subtopic_id for record in mastery_records])))}
    overdue = [record for record in mastery_records if record.revision_due_at is not None and record.revision_due_at <= now]
    if overdue:
        record = min(overdue, key=lambda item: item.revision_due_at or now)
        subtopic = subtopics[record.subtopic_id]
        return NextAction("revision", subtopic.id, subtopic.title, "This concept is due for revision to protect long-term retention.", record.mastery_score, mastery_confidence(record.evidence_count))
    prerequisite_ids = set(database.scalars(select(Prerequisite.prerequisite_subtopic_id).where(Prerequisite.subtopic_id.in_([record.subtopic_id for record in mastery_records if record.mastery_score >= 45]))))
    prerequisite_records = [record for record in mastery_records if record.subtopic_id in prerequisite_ids and record.mastery_score < 45]
    if prerequisite_records:
        record = min(prerequisite_records, key=lambda item: item.mastery_score)
        subtopic = subtopics[record.subtopic_id]
        return NextAction("remediation", subtopic.id, subtopic.title, "Strengthen this prerequisite before moving to more advanced material.", record.mastery_score, mastery_confidence(record.evidence_count))
    weak_records = [record for record in mastery_records if record.mastery_score < 45]
    if weak_records:
        record = min(weak_records, key=lambda item: item.mastery_score)
        subtopic = subtopics[record.subtopic_id]
        return NextAction("remediation", subtopic.id, subtopic.title, "Your recent assessment evidence identifies this as the weakest studied concept.", record.mastery_score, mastery_confidence(record.evidence_count))
    record = min(mastery_records, key=lambda item: (item.evidence_count, item.mastery_score))
    subtopic = subtopics[record.subtopic_id]
    return NextAction("learn", subtopic.id, subtopic.title, "More evidence here will make your learning profile more reliable.", record.mastery_score, mastery_confidence(record.evidence_count))
