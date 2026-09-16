from app.schemas.analytics import AnalyticsOverview


def test_empty_analytics_overview_is_valid() -> None:
    overview = AnalyticsOverview(questions_attempted=0, accuracy_percent=0, average_response_time_seconds=0, learning_time_minutes=0, subject_mastery=[], weak_topics=[], strong_topics=[], recent_quiz_scores=[])
    assert overview.questions_attempted == 0
