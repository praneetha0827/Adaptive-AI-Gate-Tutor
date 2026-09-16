from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AssignedTopic(Base):
    __tablename__ = "assigned_topics"
    __table_args__ = (UniqueConstraint("user_id", "subtopic_id", name="uq_assigned_topic"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="assigned")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
