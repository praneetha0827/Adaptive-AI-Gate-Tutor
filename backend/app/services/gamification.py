from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.gamification import Badge, DailyGoal, Streak, UserBadge, XPTransaction
from app.models.learning import QuestionAttempt, QuizAttempt


def level_for_xp(total_xp: int) -> int:
    return total_xp // 100 + 1


def record_learning_activity(database: Session, user_id: str, source_type: str, source_id: str, question_count: int, correct_count: int, score_percent: float | None = None) -> None:
    xp_amount = 5 + correct_count * 10
    database.add(XPTransaction(user_id=user_id, amount=xp_amount, source_type=source_type, source_id=source_id))
    today = datetime.now(UTC).date()
    streak = database.get(Streak, user_id) or Streak(user_id=user_id, current_days=0, longest_days=0)
    if streak.last_activity_date != today:
        streak.current_days = streak.current_days + 1 if streak.last_activity_date == today - timedelta(days=1) else 1
        streak.longest_days = max(streak.longest_days, streak.current_days)
        streak.last_activity_date = today
    database.add(streak)
    goal = database.scalar(select(DailyGoal).where(DailyGoal.user_id == user_id, DailyGoal.goal_date == today))
    if goal is None:
        goal = DailyGoal(user_id=user_id, goal_date=today, target_questions=10, completed_questions=0)
        database.add(goal)
    goal.completed_questions += question_count
    _award_badges(database, user_id, streak, score_percent)


def record_quiz_rewards(database: Session, user_id: str, attempt: QuizAttempt, correct_count: int, question_count: int) -> None:
    record_learning_activity(database, user_id, "quiz_attempt", attempt.id, question_count, correct_count, attempt.score_percent)


def _award_badges(database: Session, user_id: str, streak: Streak, score_percent: float | None) -> None:
    earned_codes = set(database.scalars(select(Badge.code).join(UserBadge, UserBadge.badge_id == Badge.id).where(UserBadge.user_id == user_id)))
    completed_quizzes = database.scalar(select(func.count()).select_from(QuizAttempt).where(QuizAttempt.user_id == user_id, QuizAttempt.submitted_at.is_not(None))) or 0
    attempted_questions = database.scalar(select(func.count()).select_from(QuestionAttempt).join(QuizAttempt).where(QuizAttempt.user_id == user_id)) or 0
    eligible = set()
    if completed_quizzes >= 1: eligible.add("first_quiz")
    if attempted_questions >= 100: eligible.add("hundred_questions")
    if score_percent == 100: eligible.add("perfect_quiz")
    if streak.current_days >= 7: eligible.add("seven_day_streak")
    for badge in database.scalars(select(Badge).where(Badge.code.in_(eligible - earned_codes))):
        database.add(UserBadge(user_id=user_id, badge_id=badge.id))


def progression_summary(database: Session, user_id: str) -> dict[str, object]:
    total_xp = database.scalar(select(func.coalesce(func.sum(XPTransaction.amount), 0)).where(XPTransaction.user_id == user_id)) or 0
    streak = database.get(Streak, user_id)
    today = datetime.now(UTC).date()
    goal = database.scalar(select(DailyGoal).where(DailyGoal.user_id == user_id, DailyGoal.goal_date == today))
    badges = list(database.execute(select(Badge.code, Badge.name, Badge.description).join(UserBadge, UserBadge.badge_id == Badge.id).where(UserBadge.user_id == user_id).order_by(UserBadge.earned_at.desc())).mappings())
    return {"total_xp": total_xp, "level": level_for_xp(total_xp), "xp_to_next_level": 100 - total_xp % 100, "streak_days": streak.current_days if streak else 0, "daily_goal_completed": goal.completed_questions if goal else 0, "daily_goal_target": goal.target_questions if goal else 10, "badges": [dict(badge) for badge in badges]}
