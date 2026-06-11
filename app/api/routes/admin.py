"""Admin API: user management, dataset/model management, statistics."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models.interview import Interview
from app.models.log import Log
from app.models.resume import Resume
from app.models.user import User
from app.schemas.user import UserRead
from app.services.role_predictor import RolePredictor
from app.services.training_data import ROLES, SEED_SAMPLES

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


@router.patch("/users/{user_id}/toggle-active", response_model=UserRead)
def toggle_active(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot disable your own account.")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    return {
        "users": db.scalar(select(func.count()).select_from(User)),
        "resumes": db.scalar(select(func.count()).select_from(Resume)),
        "interviews": db.scalar(select(func.count()).select_from(Interview)),
        "logs": db.scalar(select(func.count()).select_from(Log)),
    }


@router.get("/dataset")
def dataset_info(_: User = Depends(get_current_admin)):
    """Information about the training dataset behind the role model."""
    by_role = {role: sum(1 for _, r in SEED_SAMPLES if r == role) for role in ROLES}
    return {
        "roles": ROLES,
        "total_samples": len(SEED_SAMPLES),
        "samples_per_role": by_role,
    }


@router.post("/model/retrain")
def retrain_model(_: User = Depends(get_current_admin)):
    """Force the role-prediction model to retrain from the dataset."""
    RolePredictor().train()
    return {"detail": "Model retrained successfully."}


@router.get("/logs")
def recent_logs(
    limit: int = 100, db: Session = Depends(get_db), _: User = Depends(get_current_admin)
):
    rows = db.scalars(select(Log).order_by(Log.created_at.desc()).limit(limit)).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "action": r.action,
            "detail": r.detail,
            "created_at": r.created_at,
        }
        for r in rows
    ]
