"""add assigned topics

Revision ID: 20260817_08
Revises: 20260817_07
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_08"
down_revision = "20260817_07"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("assigned_topics", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("subtopic_id", sa.String(36), sa.ForeignKey("subtopics.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.UniqueConstraint("user_id", "subtopic_id", name="uq_assigned_topic"))
    op.create_index("ix_assigned_topics_user_id", "assigned_topics", ["user_id"])
    op.create_index("ix_assigned_topics_subtopic_id", "assigned_topics", ["subtopic_id"])


def downgrade() -> None:
    op.drop_index("ix_assigned_topics_subtopic_id", table_name="assigned_topics")
    op.drop_index("ix_assigned_topics_user_id", table_name="assigned_topics")
    op.drop_table("assigned_topics")
