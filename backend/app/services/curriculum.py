from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.curriculum import CurriculumStatus, CurriculumVersion, Subject, Subtopic, Topic


def list_published_versions(database: Session) -> list[CurriculumVersion]:
    statement = (
        select(CurriculumVersion)
        .where(CurriculumVersion.status == CurriculumStatus.PUBLISHED)
        .order_by(CurriculumVersion.effective_from.desc(), CurriculumVersion.label.desc())
    )
    return list(database.scalars(statement))


def list_subjects(database: Session, curriculum_version_id: str) -> list[Subject]:
    statement = (
        select(Subject)
        .where(Subject.curriculum_version_id == curriculum_version_id)
        .options(
            selectinload(Subject.topics)
            .selectinload(Topic.subtopics)
            .selectinload(Subtopic.learning_objectives)
        )
        .order_by(Subject.display_order)
    )
    return list(database.scalars(statement))
