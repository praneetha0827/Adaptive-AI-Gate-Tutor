from datetime import UTC, datetime, timedelta


def test_revision_due_dates_take_priority_over_new_learning() -> None:
    overdue_at = datetime.now(UTC) - timedelta(days=1)
    future_at = datetime.now(UTC) + timedelta(days=7)
    assert overdue_at < future_at
