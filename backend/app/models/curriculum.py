from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CurriculumStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    RETIRED = "retired"


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    versions: Mapped[list["CurriculumVersion"]] = relationship(back_populates="exam")


class CurriculumVersion(Base):
    __tablename__ = "curriculum_versions"
    __table_args__ = (UniqueConstraint("exam_id", "label", name="uq_curriculum_version_exam_label"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id", ondelete="RESTRICT"), index=True)
    label: Mapped[str] = mapped_column(String(30))
    status: Mapped[CurriculumStatus] = mapped_column(
        Enum(CurriculumStatus, values_callable=lambda status: [item.value for item in status]),
        default=CurriculumStatus.DRAFT,
    )
    official_source_url: Mapped[str | None] = mapped_column(String(2048))
    effective_from: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    exam: Mapped[Exam] = relationship(back_populates="versions")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="curriculum_version", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("curriculum_version_id", "code", name="uq_subject_version_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    curriculum_version_id: Mapped[str] = mapped_column(ForeignKey("curriculum_versions.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(150))
    display_order: Mapped[int] = mapped_column(Integer)
    curriculum_version: Mapped[CurriculumVersion] = relationship(back_populates="subjects")
    topics: Mapped[list["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("subject_id", "code", name="uq_topic_subject_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer)
    subject: Mapped[Subject] = relationship(back_populates="topics")
    subtopics: Mapped[list["Subtopic"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class Subtopic(Base):
    __tablename__ = "subtopics"
    __table_args__ = (UniqueConstraint("topic_id", "code", name="uq_subtopic_topic_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer)
    topic: Mapped[Topic] = relationship(back_populates="subtopics")
    learning_objectives: Mapped[list["LearningObjective"]] = relationship(back_populates="subtopic", cascade="all, delete-orphan")


class Prerequisite(Base):
    __tablename__ = "prerequisites"
    __table_args__ = (
        UniqueConstraint("subtopic_id", "prerequisite_subtopic_id", name="uq_prerequisite_edge"),
        CheckConstraint("subtopic_id <> prerequisite_subtopic_id", name="ck_prerequisite_not_self"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="CASCADE"), index=True)
    prerequisite_subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="RESTRICT"), index=True)


class LearningObjective(Base):
    __tablename__ = "learning_objectives"
    __table_args__ = (UniqueConstraint("subtopic_id", "code", name="uq_learning_objective_subtopic_code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subtopic_id: Mapped[str] = mapped_column(ForeignKey("subtopics.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(100))
    statement: Mapped[str] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer)
    subtopic: Mapped[Subtopic] = relationship(back_populates="learning_objectives")

