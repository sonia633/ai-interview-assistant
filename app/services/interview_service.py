"""Orchestrates interview creation, answering and scoring."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.interview import Interview
from app.models.question import Question
from app.models.resume import Resume
from app.models.score import Score
from app.models.skill import ResumeSkill, Skill
from app.services.answer_evaluator import AnswerEvaluator
from app.services.question_generator import QuestionGenerator


class InterviewService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.generator = QuestionGenerator()
        self.evaluator = AnswerEvaluator()

    # ---- creation ----
    def create_interview(
        self, user_id: int, resume_id: int | None, role: str | None, num_questions: int
    ) -> Interview:
        resume: Resume | None = None
        top_skills: list[str] = []
        has_experience = False

        if resume_id:
            resume = self.db.get(Resume, resume_id)
            if resume and resume.user_id == user_id:
                role = role or resume.predicted_role
                has_experience = bool(resume.experience)
                top_skills = self._top_skills(resume_id)

        interview = Interview(user_id=user_id, resume_id=resume_id, role=role)
        self.db.add(interview)
        self.db.flush()

        questions = self.generator.generate(role, top_skills, has_experience, num_questions)
        for q in questions:
            self.db.add(
                Question(interview_id=interview.id, category=q["category"], text=q["text"])
            )
        # Initialise an empty score row
        self.db.add(
            Score(interview_id=interview.id, total_questions=len(questions))
        )
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def _top_skills(self, resume_id: int) -> list[str]:
        rows = self.db.execute(
            select(Skill.name)
            .join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
            .where(ResumeSkill.resume_id == resume_id, Skill.category == "technical")
            .order_by(ResumeSkill.frequency.desc())
            .limit(6)
        ).all()
        return [r[0] for r in rows]

    # ---- answering ----
    def submit_answer(self, question_id: int, text: str) -> dict:
        question = self.db.get(Question, question_id)
        if question is None:
            raise ValueError("Question not found")

        result = self.evaluator.evaluate(question.text, text)

        answer = self.db.scalars(
            select(Answer).where(Answer.question_id == question_id)
        ).first()
        if answer is None:
            answer = Answer(question_id=question_id, text=text)
            self.db.add(answer)
        else:
            answer.text = text

        answer.score = result["score"]
        answer.feedback = result["feedback"]
        answer.strengths = "\n".join(result["strengths"])
        answer.weaknesses = "\n".join(result["weaknesses"])
        self.db.flush()

        self._recompute_score(question.interview_id)
        self.db.commit()

        return {"question_id": question_id, **result}

    def _recompute_score(self, interview_id: int) -> None:
        rows = self.db.execute(
            select(Answer.score)
            .join(Question, Question.id == Answer.question_id)
            .where(Question.interview_id == interview_id, Answer.score.isnot(None))
        ).all()
        answered = [r[0] for r in rows]

        total_q = self.db.scalar(
            select(Question.id).where(Question.interview_id == interview_id).limit(1)
        )
        total_count = len(
            self.db.execute(
                select(Question.id).where(Question.interview_id == interview_id)
            ).all()
        )

        score = self.db.scalars(
            select(Score).where(Score.interview_id == interview_id)
        ).first()
        if score is None:
            score = Score(interview_id=interview_id)
            self.db.add(score)

        score.total_questions = total_count
        score.answered_questions = len(answered)
        score.average_score = round(sum(answered) / len(answered), 1) if answered else 0.0

        interview = self.db.get(Interview, interview_id)
        if interview and total_count and len(answered) >= total_count:
            interview.status = "completed"
