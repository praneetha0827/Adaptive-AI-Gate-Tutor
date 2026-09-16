from typing import Literal

from pydantic import BaseModel, Field


TutorStage = Literal["hook", "explain", "worked_example", "interactive_question", "hint", "mini_challenge", "summary", "mastery_check"]


class TutorTurn(BaseModel):
    stage: TutorStage
    explanation: str = Field(min_length=1, max_length=4000)
    question: str | None = Field(default=None, max_length=1500)
    hint: str | None = Field(default=None, max_length=1500)
    difficulty: int = Field(ge=1, le=5)


class StartTutorSessionRequest(BaseModel):
    subtopic_id: str = Field(min_length=1)


class SendTutorMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=3000)


class TutorSessionResponse(BaseModel):
    session_id: str
    turn: TutorTurn

