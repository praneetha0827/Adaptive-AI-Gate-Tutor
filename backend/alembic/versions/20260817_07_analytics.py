"""add analytics events

Revision ID: 20260817_07
Revises: 20260817_06
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_07"
down_revision = "20260817_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("analytics_events", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("event_type", sa.String(50), nullable=False), sa.Column("payload", sa.JSON()), sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_analytics_events_event_type", table_name="analytics_events")
    op.drop_index("ix_analytics_events_user_id", table_name="analytics_events")
    op.drop_table("analytics_events")
