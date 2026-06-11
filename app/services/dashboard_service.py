"""Aggregate dashboard metrics for a user."""
from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.interview import Interview
from app.models.question import Question
from app.models.resume import Resume
from app.models.score import Score
from app.models.skill import ResumeSkill, Skill


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def overview(self, user_id: int) -> dict:
        interviews = list(
            self.db.scalars(
                select(Interview).where(Interview.user_id == user_id)
            ).all()
        )
        interview_ids = [i.id for i in interviews]

        scores = []
        if interview_ids:
            scores = list(
                self.db.scalars(
                    select(Score).where(Score.interview_id.in_(interview_ids))
                ).all()
            )
        avg_score = round(sum(s.average_score for s in scores) / len(scores), 1) if scores else 0.0

        # Progress over time: each completed interview's average score
        progress = [
            {
                "interview_id": s.interview_id,
                "score": round(s.average_score, 1),
            }
            for s in sorted(scores, key=lambda x: x.interview_id)
        ]

        # Skill distribution across the user's resumes
        skill_counts = self._skill_distribution(user_id)

        return {
            "total_interviews": len(interviews),
            "completed_interviews": sum(1 for i in interviews if i.status == "completed"),
            "average_score": avg_score,
            "progress": progress,
            "skill_distribution": skill_counts,
        }

    def _skill_distribution(self, user_id: int) -> dict[str, int]:
        rows = self.db.execute(
            select(Skill.name, ResumeSkill.frequency)
            .join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
            .join(Resume, Resume.id == ResumeSkill.resume_id)
            .where(Resume.user_id == user_id, Skill.category == "technical")
        ).all()
        counter: Counter[str] = Counter()
        for name, freq in rows:
            counter[name] += freq or 1
        return dict(counter.most_common(10))
