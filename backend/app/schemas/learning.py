from pydantic import BaseModel, Field, field_validator, model_validator


class OnboardingRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)
    target_exam: str = Field(default="GATE CSE", max_length=50)
    target_year: int = Field(ge=2026, le=2100)
    target_rank: int | None = Field(default=None, ge=1, le=100000)
    daily_study_minutes: int = Field(ge=15, le=960)
    programming_experience: str = Field(max_length=30)
    preferred_learning_style: str | None = Field(default=None, max_length=30)
    subject_confidence: dict[str, int] | None = None

    @field_validator("subject_confidence")
    @classmethod
    def validate_subject_confidence(cls, value: dict[str, int] | None) -> dict[str, int] | None:
        if value is None:
            return None
        if len(value) > 30 or any(not subject_id or confidence < 1 or confidence > 5 for subject_id, confidence in value.items()):
            raise ValueError("Subject confidence values must be between 1 and 5")
        return value


class StartDiagnosticRequest(BaseModel):
    curriculum_version_id: str = Field(min_length=1)
    question_limit: int = Field(default=15, ge=5, le=30)


class DiagnosticQuestionResponse(BaseModel):
    id: str
    question_type: str
    prompt: str
    options: list[dict[str, str]] | None


class DiagnosticAssessmentResponse(BaseModel):
    id: str
    status: str
    questions: list[DiagnosticQuestionResponse]


class DiagnosticAnswer(BaseModel):
    question_id: str
    answer: str = Field(max_length=500)
    response_time_ms: int = Field(ge=0, le=7_200_000)


class SubmitDiagnosticRequest(BaseModel):
    answers: list[DiagnosticAnswer] = Field(min_length=1)

    @model_validator(mode="after")
    def has_unique_questions(self) -> "SubmitDiagnosticRequest":
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Each question may be answered once")
        return self


class MasteryResponse(BaseModel):
    subtopic_id: str
    mastery_score: float
    evidence_count: int
    confidence: str
