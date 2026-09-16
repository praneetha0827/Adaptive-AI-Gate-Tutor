"""add quiz attempts and mistakes

Revision ID: 20260817_05
Revises: 20260817_04
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_05"
down_revision = "20260817_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("concept", sa.String(150), nullable=True))
    op.add_column("questions", sa.Column("skill_tested", sa.String(150), nullable=True))
    op.execute("UPDATE questions SET concept = 'unclassified', skill_tested = 'practice' WHERE concept IS NULL OR skill_tested IS NULL")
    op.alter_column("questions", "concept", nullable=False)
    op.alter_column("questions", "skill_tested", nullable=False)
    op.create_table("quizzes", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(150), nullable=False), sa.Column("time_limit_seconds", sa.Integer()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_quizzes_user_id", "quizzes", ["user_id"])
    op.create_table("quiz_questions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("quiz_id", sa.String(36), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False), sa.Column("display_order", sa.Integer(), nullable=False), sa.UniqueConstraint("quiz_id", "question_id", name="uq_quiz_question"))
    op.create_index("ix_quiz_questions_quiz_id", "quiz_questions", ["quiz_id"])
    op.create_index("ix_quiz_questions_question_id", "quiz_questions", ["question_id"])
    op.create_table("quiz_attempts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("quiz_id", sa.String(36), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("score_percent", sa.Float()))
    op.create_index("ix_quiz_attempts_quiz_id", "quiz_attempts", ["quiz_id"])
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_table("question_attempts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("quiz_attempt_id", sa.String(36), sa.ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False), sa.Column("submitted_answer", sa.Text()), sa.Column("is_correct", sa.Boolean()), sa.Column("response_time_ms", sa.Integer()), sa.UniqueConstraint("quiz_attempt_id", "question_id", name="uq_quiz_attempt_question"))
    op.create_index("ix_question_attempts_quiz_attempt_id", "question_attempts", ["quiz_attempt_id"])
    op.create_index("ix_question_attempts_question_id", "question_attempts", ["question_id"])
    op.create_table("mistakes", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("question_attempt_id", sa.String(36), sa.ForeignKey("question_attempts.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="RESTRICT"), nullable=False), sa.Column("concept", sa.String(150), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_mistakes_user_id", "mistakes", ["user_id"])
    op.create_index("ix_mistakes_question_attempt_id", "mistakes", ["question_attempt_id"])
    op.create_index("ix_mistakes_subtopic_id", "mistakes", ["subtopic_id"])


def downgrade() -> None:
    for table, index in (("mistakes", "ix_mistakes_subtopic_id"), ("mistakes", "ix_mistakes_question_attempt_id"), ("mistakes", "ix_mistakes_user_id"), ("question_attempts", "ix_question_attempts_question_id"), ("question_attempts", "ix_question_attempts_quiz_attempt_id"), ("quiz_attempts", "ix_quiz_attempts_user_id"), ("quiz_attempts", "ix_quiz_attempts_quiz_id"), ("quiz_questions", "ix_quiz_questions_question_id"), ("quiz_questions", "ix_quiz_questions_quiz_id"), ("quizzes", "ix_quizzes_user_id")):
        op.drop_index(index, table_name=table)
    for table in ("mistakes", "question_attempts", "quiz_attempts", "quiz_questions", "quizzes"):
        op.drop_table(table)
    op.drop_column("questions", "skill_tested")
    op.drop_column("questions", "concept")
