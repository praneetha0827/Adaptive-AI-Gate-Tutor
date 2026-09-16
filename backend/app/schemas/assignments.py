from typing import Literal

from pydantic import BaseModel, Field


class AssignTopicRequest(BaseModel):
    subtopic_id: str = Field(min_length=1)


class AssignTopicResponse(BaseModel):
    status: Literal["assigned", "blocked"]
    subtopic_id: str
    reason: str
    prerequisite_subtopic_id: str | None = None
