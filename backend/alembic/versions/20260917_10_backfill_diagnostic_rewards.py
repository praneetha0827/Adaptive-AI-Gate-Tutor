"""backfill rewards for completed diagnostics

Revision ID: 20260917_10
Revises: 20260914_09
Create Date: 2026-09-17
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "20260917_10"
down_revision = "20260914_09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    diagnostics = connection.execute(sa.text("""
        SELECT assessment.id, assessment.user_id, assessment.completed_at,
               COUNT(attempt.id) AS question_count,
               COUNT(attempt.id) FILTER (WHERE attempt.is_correct) AS correct_count
        FROM diagnostic_assessments AS assessment
        JOIN diagnostic_attempts AS attempt ON attempt.diagnostic_assessment_id = assessment.id
        WHERE assessment.status = 'completed' AND assessment.completed_at IS NOT NULL
        GROUP BY assessment.id, assessment.user_id, assessment.completed_at
    """)).mappings()
    for diagnostic in diagnostics:
        existing = connection.scalar(sa.text("SELECT 1 FROM xp_transactions WHERE user_id = :user_id AND source_type = 'diagnostic' AND source_id = :source_id"), {"user_id": diagnostic["user_id"], "source_id": diagnostic["id"]})
        if existing:
            continue
        completed_on = diagnostic["completed_at"].date()
        connection.execute(sa.text("""
            INSERT INTO xp_transactions (id, user_id, amount, source_type, source_id, created_at)
            VALUES (:id, :user_id, :amount, 'diagnostic', :source_id, :completed_at)
        """), {"id": str(uuid4()), "user_id": diagnostic["user_id"], "amount": 5 + diagnostic["correct_count"] * 10, "source_id": diagnostic["id"], "completed_at": diagnostic["completed_at"]})
        connection.execute(sa.text("""
            INSERT INTO daily_goals (id, user_id, goal_date, target_questions, completed_questions)
            VALUES (:id, :user_id, :goal_date, 10, :question_count)
            ON CONFLICT (user_id, goal_date) DO UPDATE
            SET completed_questions = daily_goals.completed_questions + EXCLUDED.completed_questions
        """), {"id": str(uuid4()), "user_id": diagnostic["user_id"], "goal_date": completed_on, "question_count": diagnostic["question_count"]})
        connection.execute(sa.text("""
            INSERT INTO streaks (user_id, current_days, longest_days, last_activity_date)
            VALUES (:user_id, 1, 1, :activity_date)
            ON CONFLICT (user_id) DO NOTHING
        """), {"user_id": diagnostic["user_id"], "activity_date": completed_on})


def downgrade() -> None:
    pass
