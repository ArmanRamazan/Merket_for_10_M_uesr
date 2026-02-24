from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ModelTier(StrEnum):
    CHEAP = "cheap"
    MID = "mid"
    EXPENSIVE = "expensive"


MODEL_TIER_MAP: dict[str, ModelTier] = {
    "quiz": ModelTier.CHEAP,
    "summary": ModelTier.CHEAP,
}


class QuestionData(BaseModel):
    text: str
    options: list[str] = Field(min_length=2, max_length=6)
    correct_index: int
    explanation: str


class QuizRequest(BaseModel):
    lesson_id: UUID
    content: str = Field(min_length=10, max_length=50000)


class QuizResponse(BaseModel):
    lesson_id: UUID
    questions: list[QuestionData]
    model_used: str
    cached: bool


class SummaryRequest(BaseModel):
    lesson_id: UUID
    content: str = Field(min_length=10, max_length=50000)


class SummaryResponse(BaseModel):
    lesson_id: UUID
    summary: str
    model_used: str
    cached: bool
