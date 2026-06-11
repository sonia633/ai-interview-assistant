"""Interview API routes: create session, fetch questions, submit answers."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.log import Log
from app.models.user import User
from app.repositories.interview_repo import InterviewRepository
from app.schemas.interview import (
    AnswerEvaluation,
    AnswerSubmit,
    InterviewCreate,
    InterviewRead,
    QuestionRead,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/api/interviews", tags=["interviews"])


@router.post("", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = InterviewService(db)
    interview = service.create_interview(
        user_id=user.id,
        resume_id=data.resume_id,
        role=data.role,
        num_questions=data.num_questions,
    )
    db.add(Log(user_id=user.id, action="interview_create", detail=f"interview={interview.id}"))
    db.commit()
    return interview


@router.get("", response_model=list[InterviewRead])
def list_interviews(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return InterviewRepository(db).list_for_user(user.id)


@router.get("/{interview_id}/questions", response_model=list[QuestionRead])
def get_questions(
    interview_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repo = InterviewRepository(db)
    interview = repo.get(interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview.questions


@router.post("/answers", response_model=AnswerEvaluation)
def submit_answer(
    data: AnswerSubmit,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    repo = InterviewRepository(db)
    question = repo.get_question(data.question_id)
    if not question or question.interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Question not found")

    service = InterviewService(db)
    result = service.submit_answer(data.question_id, data.text)
    return AnswerEvaluation(**result)
