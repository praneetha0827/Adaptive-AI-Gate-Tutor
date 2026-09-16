"""add tutor sessions

Revision ID: 20260817_04
Revises: 20260817_03
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_04"
down_revision = "20260817_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tutor_sessions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="RESTRICT"), nullable=False), sa.Column("context_snapshot", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("closed_at", sa.DateTime(timezone=True)))
    op.create_index("ix_tutor_sessions_user_id", "tutor_sessions", ["user_id"])
    op.create_index("ix_tutor_sessions_subtopic_id", "tutor_sessions", ["subtopic_id"])
    op.create_table("tutor_messages", sa.Column("id", sa.String(36), primary_key=True), sa.Column("session_id", sa.String(36), sa.ForeignKey("tutor_sessions.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("structured_turn", sa.JSON()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_tutor_messages_session_id", "tutor_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_tutor_messages_session_id", table_name="tutor_messages")
    op.drop_table("tutor_messages")
    op.drop_index("ix_tutor_sessions_subtopic_id", table_name="tutor_sessions")
    op.drop_index("ix_tutor_sessions_user_id", table_name="tutor_sessions")
    op.drop_table("tutor_sessions")

