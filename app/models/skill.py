"""Skill catalogue and resume-skill association (frequency)."""
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Skill(Base):
    """Canonical skill (technical or soft)."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(20), default="technical")  # technical | soft

    resume_links: Mapped[list["ResumeSkill"]] = relationship(back_populates="skill")


class ResumeSkill(Base):
    """Association: a skill found in a resume, with frequency."""

    __tablename__ = "resume_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    frequency: Mapped[int] = mapped_column(Integer, default=1)

    resume: Mapped["Resume"] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship(back_populates="resume_links")
