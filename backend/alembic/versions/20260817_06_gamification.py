"""add deterministic gamification

Revision ID: 20260817_06
Revises: 20260817_05
Create Date: 2026-08-17
"""

from alembic import op
import sqlalchemy as sa

revision = "20260817_06"
down_revision = "20260817_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("xp_transactions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("amount", sa.Integer(), nullable=False), sa.Column("source_type", sa.String(30), nullable=False), sa.Column("source_id", sa.String(36), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.UniqueConstraint("user_id", "source_type", "source_id", name="uq_xp_source"))
    op.create_index("ix_xp_transactions_user_id", "xp_transactions", ["user_id"])
    op.create_table("badges", sa.Column("id", sa.String(36), primary_key=True), sa.Column("code", sa.String(50), nullable=False, unique=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("description", sa.String(255), nullable=False))
    op.bulk_insert(sa.table("badges", sa.column("id", sa.String), sa.column("code", sa.String), sa.column("name", sa.String), sa.column("description", sa.String)), [{"id": "a0000000-0000-0000-0000-000000000001", "code": "first_quiz", "name": "First Quiz", "description": "Complete your first quiz."}, {"id": "a0000000-0000-0000-0000-000000000002", "code": "hundred_questions", "name": "100 Questions", "description": "Attempt 100 quiz questions."}, {"id": "a0000000-0000-0000-0000-000000000003", "code": "perfect_quiz", "name": "Perfect Quiz", "description": "Score 100% on a quiz."}, {"id": "a0000000-0000-0000-0000-000000000004", "code": "seven_day_streak", "name": "7-Day Streak", "description": "Study on seven consecutive days."}])
    op.create_table("user_badges", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("badge_id", sa.String(36), sa.ForeignKey("badges.id", ondelete="CASCADE"), nullable=False), sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"))
    op.create_index("ix_user_badges_user_id", "user_badges", ["user_id"])
    op.create_index("ix_user_badges_badge_id", "user_badges", ["badge_id"])
    op.create_table("streaks", sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("current_days", sa.Integer(), nullable=False), sa.Column("longest_days", sa.Integer(), nullable=False), sa.Column("last_activity_date", sa.Date()))
    op.create_table("daily_goals", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("goal_date", sa.Date(), nullable=False), sa.Column("target_questions", sa.Integer(), nullable=False), sa.Column("completed_questions", sa.Integer(), nullable=False), sa.UniqueConstraint("user_id", "goal_date", name="uq_daily_goal_user_date"))
    op.create_index("ix_daily_goals_user_id", "daily_goals", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_daily_goals_user_id", table_name="daily_goals")
    op.drop_table("daily_goals")
    op.drop_table("streaks")
    op.drop_index("ix_user_badges_badge_id", table_name="user_badges")
    op.drop_index("ix_user_badges_user_id", table_name="user_badges")
    op.drop_table("user_badges")
    op.drop_table("badges")
    op.drop_index("ix_xp_transactions_user_id", table_name="xp_transactions")
    op.drop_table("xp_transactions")
