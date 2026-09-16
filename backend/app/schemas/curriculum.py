from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class LearningObjectiveResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    statement: str
    display_order: int


class SubtopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: str | None
    display_order: int
    learning_objectives: list[LearningObjectiveResponse]


class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: str | None
    display_order: int
    subtopics: list[SubtopicResponse]


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    display_order: int
    topics: list[TopicResponse]


class CurriculumVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    status: Literal["draft", "published", "retired"]
    official_source_url: str | None
    effective_from: date | None

