"""Interview question model."""
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True
    )
    category: Mapped[str] = mapped_column(String(30), default="technical")  # technical | behavioral | problem_solving
    text: Mapped[str] = mapped_column(Text, nullable=False)

    interview: Mapped["Interview"] = relationship(back_populates="questions")
    answer: Mapped["Answer"] = relationship(
        back_populates="question", uselist=False, cascade="all, delete-orphan"
    )
