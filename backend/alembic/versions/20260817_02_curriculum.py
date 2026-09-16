"""add versioned curriculum

Revision ID: 20260817_02
Revises: 20260817_01
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_02"
down_revision = "20260817_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    curriculum_status = sa.Enum("draft", "published", "retired", name="curriculumstatus")
    op.create_table("exams", sa.Column("id", sa.String(36), primary_key=True), sa.Column("code", sa.String(30), nullable=False, unique=True), sa.Column("name", sa.String(150), nullable=False))
    op.create_index("ix_exams_code", "exams", ["code"])
    op.create_table("curriculum_versions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("exam_id", sa.String(36), sa.ForeignKey("exams.id", ondelete="RESTRICT"), nullable=False), sa.Column("label", sa.String(30), nullable=False), sa.Column("status", curriculum_status, nullable=False), sa.Column("official_source_url", sa.String(2048)), sa.Column("effective_from", sa.Date()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.UniqueConstraint("exam_id", "label", name="uq_curriculum_version_exam_label"))
    op.create_index("ix_curriculum_versions_exam_id", "curriculum_versions", ["exam_id"])
    op.create_table("subjects", sa.Column("id", sa.String(36), primary_key=True), sa.Column("curriculum_version_id", sa.String(36), sa.ForeignKey("curriculum_versions.id", ondelete="CASCADE"), nullable=False), sa.Column("code", sa.String(50), nullable=False), sa.Column("title", sa.String(150), nullable=False), sa.Column("display_order", sa.Integer(), nullable=False), sa.UniqueConstraint("curriculum_version_id", "code", name="uq_subject_version_code"))
    op.create_index("ix_subjects_curriculum_version_id", "subjects", ["curriculum_version_id"])
    op.create_table("topics", sa.Column("id", sa.String(36), primary_key=True), sa.Column("subject_id", sa.String(36), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False), sa.Column("code", sa.String(80), nullable=False), sa.Column("title", sa.String(150), nullable=False), sa.Column("description", sa.Text()), sa.Column("display_order", sa.Integer(), nullable=False), sa.UniqueConstraint("subject_id", "code", name="uq_topic_subject_code"))
    op.create_index("ix_topics_subject_id", "topics", ["subject_id"])
    op.create_table("subtopics", sa.Column("id", sa.String(36), primary_key=True), sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False), sa.Column("code", sa.String(100), nullable=False), sa.Column("title", sa.String(150), nullable=False), sa.Column("description", sa.Text()), sa.Column("display_order", sa.Integer(), nullable=False), sa.UniqueConstraint("topic_id", "code", name="uq_subtopic_topic_code"))
    op.create_index("ix_subtopics_topic_id", "subtopics", ["topic_id"])
    op.create_table("prerequisites", sa.Column("id", sa.String(36), primary_key=True), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="CASCADE"), nullable=False), sa.Column("prerequisite_subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="RESTRICT"), nullable=False), sa.CheckConstraint("subtopic_id <> prerequisite_subtopic_id", name="ck_prerequisite_not_self"), sa.UniqueConstraint("subtopic_id", "prerequisite_subtopic_id", name="uq_prerequisite_edge"))
    op.create_index("ix_prerequisites_subtopic_id", "prerequisites", ["subtopic_id"])
    op.create_index("ix_prerequisites_prerequisite_subtopic_id", "prerequisites", ["prerequisite_subtopic_id"])
    op.create_table("learning_objectives", sa.Column("id", sa.String(36), primary_key=True), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="CASCADE"), nullable=False), sa.Column("code", sa.String(100), nullable=False), sa.Column("statement", sa.Text(), nullable=False), sa.Column("display_order", sa.Integer(), nullable=False), sa.UniqueConstraint("subtopic_id", "code", name="uq_learning_objective_subtopic_code"))
    op.create_index("ix_learning_objectives_subtopic_id", "learning_objectives", ["subtopic_id"])


def downgrade() -> None:
    for table, index in (("learning_objectives", "ix_learning_objectives_subtopic_id"), ("prerequisites", "ix_prerequisites_prerequisite_subtopic_id"), ("prerequisites", "ix_prerequisites_subtopic_id"), ("subtopics", "ix_subtopics_topic_id"), ("topics", "ix_topics_subject_id"), ("subjects", "ix_subjects_curriculum_version_id"), ("curriculum_versions", "ix_curriculum_versions_exam_id"), ("exams", "ix_exams_code")):
        op.drop_index(index, table_name=table)
    for table in ("learning_objectives", "prerequisites", "subtopics", "topics", "subjects", "curriculum_versions", "exams"):
        op.drop_table(table)
    sa.Enum(name="curriculumstatus").drop(op.get_bind(), checkfirst=True)

