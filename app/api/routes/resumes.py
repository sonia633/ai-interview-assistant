"""Resume upload + parsing API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.log import Log
from app.models.resume import Resume
from app.models.user import User
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import ResumeRead
from app.services.resume_parser import ResumeParser
from app.services.role_predictor import RolePredictor
from app.services.storage_service import StorageService, UploadValidationError

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    storage = StorageService()
    content = await file.read()
    try:
        storage.validate(file, len(content))
    except UploadValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    stored_path, size = storage.save(file, content)

    # Parse + predict role
    parser = ResumeParser()
    parsed = parser.parse(stored_path)
    predictor = RolePredictor()
    role, confidence = predictor.predict(
        " ".join(list(parsed.technical_skills) * 2) + " " + parsed.raw_text
    )

    repo = ResumeRepository(db)
    resume = Resume(
        user_id=user.id,
        original_filename=file.filename or "resume.pdf",
        stored_path=stored_path,
        file_size=size,
        candidate_name=parsed.candidate_name,
        email=parsed.email,
        phone=parsed.phone,
        education=parsed.education,
        experience=parsed.experience,
        languages=parsed.languages,
        raw_text=parsed.raw_text,
        predicted_role=role,
        role_confidence=round(confidence, 4),
    )
    resume = repo.add(resume)
    repo.attach_skills(resume, parsed.technical_skills, "technical")
    repo.attach_skills(resume, parsed.soft_skills, "soft")

    db.add(Log(user_id=user.id, action="resume_upload", detail=resume.original_filename))
    db.commit()
    return resume


@router.get("", response_model=list[ResumeRead])
def list_resumes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ResumeRepository(db).list_for_user(user.id)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
    resume_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = ResumeRepository(db).get(resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
