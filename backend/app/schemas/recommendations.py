from typing import Literal

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    action: Literal["diagnostic", "revision", "remediation", "learn"]
    subtopic_id: str | None
    subtopic_title: str | None
    reason: str
    mastery_score: float | None
    confidence: str | None
