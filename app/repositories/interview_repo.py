"""Interview / question / answer repositories."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.interview import Interview
from app.models.question import Question
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[Interview]):
    model = Interview

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_user(self, user_id: int) -> list[Interview]:
        stmt = (
            select(Interview)
            .where(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_question(self, question_id: int) -> Question | None:
        return self.db.get(Question, question_id)

    def get_answer_for_question(self, question_id: int) -> Answer | None:
        stmt = select(Answer).where(Answer.question_id == question_id)
        return self.db.scalars(stmt).first()
