from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignments import AssignedTopic
from app.models.curriculum import Prerequisite, Subtopic
from app.models.learning import StudentMastery


def get_unmet_prerequisite(database: Session, user_id: str, subtopic_id: str) -> Subtopic | None:
    prerequisite_ids = list(database.scalars(select(Prerequisite.prerequisite_subtopic_id).where(Prerequisite.subtopic_id == subtopic_id)))
    if not prerequisite_ids:
        return None
    mastery = {record.subtopic_id: record for record in database.scalars(select(StudentMastery).where(StudentMastery.user_id == user_id, StudentMastery.subtopic_id.in_(prerequisite_ids)))}
    for prerequisite_id in prerequisite_ids:
        if mastery.get(prerequisite_id) is None or mastery[prerequisite_id].mastery_score < 45:
            return database.get(Subtopic, prerequisite_id)
    return None


def assign_topic(database: Session, user_id: str, subtopic_id: str) -> tuple[str, str, str | None]:
    subtopic = database.get(Subtopic, subtopic_id)
    if subtopic is None:
        raise LookupError("Subtopic not found")
    prerequisite = get_unmet_prerequisite(database, user_id, subtopic_id)
    if prerequisite is not None:
        return "blocked", f"Study the prerequisite {prerequisite.title} first.", prerequisite.id
    assignment = database.scalar(select(AssignedTopic).where(AssignedTopic.user_id == user_id, AssignedTopic.subtopic_id == subtopic_id))
    if assignment is None:
        database.add(AssignedTopic(user_id=user_id, subtopic_id=subtopic_id))
        database.commit()
    return "assigned", f"{subtopic.title} has been added to your learning path.", None
