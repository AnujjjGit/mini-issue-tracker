"""Dashboard aggregate counts scoped to the current user."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database import get_db
from app.models import Issue, Project, User
from app.schemas.dashboard import DashboardResponse
from app.schemas.enums import COMPLETED_STATUSES, OPEN_STATUSES

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DashboardResponse:
    total_projects = db.scalar(select(func.count()).select_from(Project).where(Project.owner_id == current_user.id))
    issue_count_base = select(func.count()).select_from(Issue).join(Project, Issue.project_id == Project.id).where(Project.owner_id == current_user.id)
    total_issues = db.scalar(issue_count_base)
    open_issues = db.scalar(issue_count_base.where(Issue.status.in_(OPEN_STATUSES)))
    completed_issues = db.scalar(issue_count_base.where(Issue.status.in_(COMPLETED_STATUSES)))
    return DashboardResponse(total_projects=total_projects or 0, total_issues=total_issues or 0, open_issues=open_issues or 0, completed_issues=completed_issues or 0)
