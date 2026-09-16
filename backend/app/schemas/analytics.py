from pydantic import BaseModel


class MasteryRollup(BaseModel):
    id: str
    title: str
    mastery_score: float


class RecentQuizScore(BaseModel):
    quiz_id: str
    score_percent: float
    submitted_at: str


class AnalyticsOverview(BaseModel):
    questions_attempted: int
    accuracy_percent: float
    average_response_time_seconds: float
    learning_time_minutes: int
    subject_mastery: list[MasteryRollup]
    weak_topics: list[MasteryRollup]
    strong_topics: list[MasteryRollup]
    recent_quiz_scores: list[RecentQuizScore]
