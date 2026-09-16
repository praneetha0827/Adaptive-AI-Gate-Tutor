from pydantic import BaseModel, Field, model_validator


class CreateQuizRequest(BaseModel):
    subtopic_ids: list[str] = Field(min_length=1, max_length=10)
    question_count: int = Field(ge=1, le=50)
    title: str = Field(default="Practice quiz", min_length=1, max_length=150)
    time_limit_seconds: int | None = Field(default=None, ge=60, le=21_600)


class QuizQuestionResponse(BaseModel):
    id: str
    question_type: str
    prompt: str
    options: list[dict[str, str]] | None
    difficulty: int


class QuizResponse(BaseModel):
    quiz_id: str
    attempt_id: str
    title: str
    questions: list[QuizQuestionResponse]


class QuizAnswer(BaseModel):
    question_id: str
    answer: str = Field(max_length=500)
    response_time_ms: int = Field(ge=0, le=7_200_000)


class SubmitQuizRequest(BaseModel):
    answers: list[QuizAnswer] = Field(min_length=1)

    @model_validator(mode="after")
    def has_unique_questions(self) -> "SubmitQuizRequest":
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Each question may be answered once")
        return self


class QuizQuestionReview(BaseModel):
    prompt: str
    submitted_answer: str
    correct_answer: str
    explanation: str
    is_correct: bool


class QuizResultResponse(BaseModel):
    score_percent: float
    correct_count: int
    question_count: int
    mistakes_created: int
    reviews: list[QuizQuestionReview]
