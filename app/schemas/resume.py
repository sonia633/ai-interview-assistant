"""Resume-related Pydantic schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    category: str
    frequency: int


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    candidate_name: str | None
    email: str | None
    phone: str | None
    education: str | None
    experience: str | None
    languages: str | None
    predicted_role: str | None
    role_confidence: float | None
    created_at: datetime


class ParsedResume(BaseModel):
    candidate_name: str | None = None
    email: str | None = None
    phone: str | None = None
    education: str | None = None
    experience: str | None = None
    languages: str | None = None
    raw_text: str = ""
    technical_skills: dict[str, int] = {}
    soft_skills: dict[str, int] = {}
