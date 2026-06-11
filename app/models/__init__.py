"""Import all models so SQLAlchemy + Alembic can discover them."""
from app.models.user import User
from app.models.resume import Resume
from app.models.skill import Skill, ResumeSkill
from app.models.interview import Interview
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app.models.log import Log

__all__ = [
    "User",
    "Resume",
    "Skill",
    "ResumeSkill",
    "Interview",
    "Question",
    "Answer",
    "Score",
    "Log",
]
