"""Interview-related Pydantic schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    text: str


class AnswerSubmit(BaseModel):
    question_id: int
    text: str = Field(min_length=1, max_length=5000)


class AnswerEvaluation(BaseModel):
    question_id: int
    score: float
    feedback: str
    strengths: list[str]
    weaknesses: list[str]


class InterviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str | None
    status: str
    created_at: datetime


class InterviewCreate(BaseModel):
    resume_id: int | None = None
    role: str | None = None
    num_questions: int = Field(default=6, ge=3, le=20)
