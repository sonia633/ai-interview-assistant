"""Server-rendered HTML pages (Jinja2 + Bootstrap)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional
from app.core.database import get_db
from app.models.user import User
from app.repositories.interview_repo import InterviewRepository
from app.repositories.resume_repo import ResumeRepository
from app.services.dashboard_service import DashboardService
from app.templating import templates

router = APIRouter(tags=["pages"])


def _ctx(request: Request, user: User | None, **extra):
    base = {"request": request, "user": user}
    base.update(extra)
    return base


@router.get("/", response_class=HTMLResponse)
def home(request: Request, user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "index.html", _ctx(request, user))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "login.html", _ctx(request, user))


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "register.html", _ctx(request, user))


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)
    overview = DashboardService(db).overview(user.id)
    resumes = ResumeRepository(db).list_for_user(user.id)
    interviews = InterviewRepository(db).list_for_user(user.id)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        _ctx(request, user, overview=overview, resumes=resumes, interviews=interviews),
    )


@router.get("/resumes", response_class=HTMLResponse)
def resumes_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)
    resumes = ResumeRepository(db).list_for_user(user.id)
    return templates.TemplateResponse(request, "resumes.html", _ctx(request, user, resumes=resumes))


@router.get("/interview", response_class=HTMLResponse)
def interview_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)
    resumes = ResumeRepository(db).list_for_user(user.id)
    return templates.TemplateResponse(request, "interview.html", _ctx(request, user, resumes=resumes))


@router.get("/history", response_class=HTMLResponse)
def history_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)
    interviews = InterviewRepository(db).list_for_user(user.id)
    return templates.TemplateResponse(
        request, "history.html", _ctx(request, user, interviews=interviews)
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_page(
    request: Request,
    user: User | None = Depends(get_current_user_optional),
):
    if not user:
        return RedirectResponse("/login", status_code=302)
    if not user.is_admin:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse(request, "admin.html", _ctx(request, user))
