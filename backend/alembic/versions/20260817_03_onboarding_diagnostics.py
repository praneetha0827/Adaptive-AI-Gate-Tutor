"""add onboarding, diagnostics, and mastery

Revision ID: 20260817_03
Revises: 20260817_02
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_03"
down_revision = "20260817_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("target_rank", sa.Integer()))
    op.add_column("profiles", sa.Column("programming_experience", sa.String(30)))
    op.add_column("profiles", sa.Column("preferred_learning_style", sa.String(30)))
    op.add_column("profiles", sa.Column("onboarding_completed_at", sa.DateTime(timezone=True)))
    op.create_table("questions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="RESTRICT"), nullable=False), sa.Column("source", sa.String(30), nullable=False), sa.Column("question_type", sa.String(10), nullable=False), sa.Column("prompt", sa.Text(), nullable=False), sa.Column("options", sa.JSON()), sa.Column("correct_answer", sa.Text(), nullable=False), sa.Column("explanation", sa.Text(), nullable=False), sa.Column("difficulty", sa.Integer(), nullable=False), sa.Column("is_diagnostic_eligible", sa.Boolean(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.CheckConstraint("difficulty BETWEEN 1 AND 5", name="ck_question_difficulty"))
    op.create_index("ix_questions_subtopic_id", "questions", ["subtopic_id"])
    op.create_index("ix_questions_is_diagnostic_eligible", "questions", ["is_diagnostic_eligible"])
    op.create_table("diagnostic_assessments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("curriculum_version_id", sa.String(36), sa.ForeignKey("curriculum_versions.id", ondelete="RESTRICT"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_diagnostic_assessments_user_id", "diagnostic_assessments", ["user_id"])
    op.create_index("ix_diagnostic_assessments_curriculum_version_id", "diagnostic_assessments", ["curriculum_version_id"])
    op.create_table("diagnostic_attempts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("diagnostic_assessment_id", sa.String(36), sa.ForeignKey("diagnostic_assessments.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False), sa.Column("submitted_answer", sa.Text()), sa.Column("is_correct", sa.Boolean()), sa.Column("response_time_ms", sa.Integer()), sa.Column("answered_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("diagnostic_assessment_id", "question_id", name="uq_diagnostic_question"))
    op.create_index("ix_diagnostic_attempts_diagnostic_assessment_id", "diagnostic_attempts", ["diagnostic_assessment_id"])
    op.create_index("ix_diagnostic_attempts_question_id", "diagnostic_attempts", ["question_id"])
    op.create_table("student_mastery", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="CASCADE"), nullable=False), sa.Column("mastery_score", sa.Float(), nullable=False), sa.Column("evidence_count", sa.Integer(), nullable=False), sa.Column("correct_count", sa.Integer(), nullable=False), sa.Column("average_response_time_ms", sa.Integer()), sa.Column("last_assessed_at", sa.DateTime(timezone=True)), sa.Column("revision_due_at", sa.DateTime(timezone=True)), sa.CheckConstraint("mastery_score BETWEEN 0 AND 100", name="ck_student_mastery_score"), sa.UniqueConstraint("user_id", "subtopic_id", name="uq_student_mastery_user_subtopic"))
    op.create_index("ix_student_mastery_user_id", "student_mastery", ["user_id"])
    op.create_index("ix_student_mastery_subtopic_id", "student_mastery", ["subtopic_id"])


def downgrade() -> None:
    for table, index in (("student_mastery", "ix_student_mastery_subtopic_id"), ("student_mastery", "ix_student_mastery_user_id"), ("diagnostic_attempts", "ix_diagnostic_attempts_question_id"), ("diagnostic_attempts", "ix_diagnostic_attempts_diagnostic_assessment_id"), ("diagnostic_assessments", "ix_diagnostic_assessments_curriculum_version_id"), ("diagnostic_assessments", "ix_diagnostic_assessments_user_id"), ("questions", "ix_questions_is_diagnostic_eligible"), ("questions", "ix_questions_subtopic_id")):
        op.drop_index(index, table_name=table)
    for table in ("student_mastery", "diagnostic_attempts", "diagnostic_assessments", "questions"):
        op.drop_table(table)
    op.drop_column("profiles", "onboarding_completed_at")
    op.drop_column("profiles", "preferred_learning_style")
    op.drop_column("profiles", "programming_experience")
    op.drop_column("profiles", "target_rank")

