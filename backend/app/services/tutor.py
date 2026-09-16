from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import Subtopic, Topic
from app.models.learning import StudentMastery
from app.models.tutor import TutorMessage, TutorSession
from app.providers.base import TutorProvider
from app.schemas.tutor import TutorTurn


def build_tutor_context(database: Session, user_id: str, subtopic_id: str) -> dict[str, object]:
    subtopic = database.get(Subtopic, subtopic_id)
    if subtopic is None:
        raise LookupError("Subtopic not found")
    topic = database.get(Topic, subtopic.topic_id)
    mastery = database.scalar(select(StudentMastery).where(StudentMastery.user_id == user_id, StudentMastery.subtopic_id == subtopic_id))
    return {"topic": topic.title if topic else None, "subtopic": subtopic.title, "description": subtopic.description, "mastery_score": mastery.mastery_score if mastery else None, "evidence_count": mastery.evidence_count if mastery else 0}


def create_session(database: Session, user_id: str, subtopic_id: str, provider: TutorProvider) -> tuple[TutorSession, TutorTurn]:
    context = build_tutor_context(database, user_id, subtopic_id)
    turn = provider.generate_tutor_turn(context, "Start the lesson with a short hook.")
    session = TutorSession(user_id=user_id, subtopic_id=subtopic_id, context_snapshot=context)
    database.add(session)
    database.flush()
    database.add(TutorMessage(session_id=session.id, role="assistant", content=turn.explanation, structured_turn=turn.model_dump()))
    database.commit()
    database.refresh(session)
    return session, turn


def continue_session(database: Session, user_id: str, session_id: str, message: str, provider: TutorProvider) -> TutorTurn:
    session = database.get(TutorSession, session_id)
    if session is None or session.user_id != user_id:
        raise LookupError("Tutor session not found")
    database.add(TutorMessage(session_id=session.id, role="user", content=message))
    turn = provider.generate_tutor_turn(session.context_snapshot, message)
    database.add(TutorMessage(session_id=session.id, role="assistant", content=turn.explanation, structured_turn=turn.model_dump()))
    database.commit()
    return turn

