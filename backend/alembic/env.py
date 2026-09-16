from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base
from app.models.user import Profile, User  # noqa: F401
from app.models.curriculum import (  # noqa: F401
    CurriculumVersion,
    Exam,
    LearningObjective,
    Prerequisite,
    Subject,
    Subtopic,
    Topic,
)
from app.models.learning import DiagnosticAssessment, DiagnosticAttempt, Mistake, Question, QuestionAttempt, Quiz, QuizAttempt, QuizQuestion, StudentMastery  # noqa: F401
from app.models.tutor import TutorMessage, TutorSession  # noqa: F401
from app.models.gamification import Badge, DailyGoal, Streak, UserBadge, XPTransaction  # noqa: F401
from app.models.analytics import AnalyticsEvent  # noqa: F401
from app.models.assignments import AssignedTopic  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
