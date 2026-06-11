"""Resume + skill repositories."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.skill import ResumeSkill, Skill
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    model = Resume

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_user(self, user_id: int) -> list[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_or_create_skill(self, name: str, category: str) -> Skill:
        name = name.strip().lower()
        skill = self.db.scalars(select(Skill).where(Skill.name == name)).first()
        if skill is None:
            skill = Skill(name=name, category=category)
            self.db.add(skill)
            self.db.flush()
        return skill

    def attach_skills(self, resume: Resume, skills: dict[str, int], category: str) -> None:
        for name, freq in skills.items():
            skill = self.get_or_create_skill(name, category)
            link = ResumeSkill(resume_id=resume.id, skill_id=skill.id, frequency=freq)
            self.db.add(link)
        self.db.commit()
