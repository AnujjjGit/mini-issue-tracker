"""Issue endpoints: create, search/filter, view, edit, assign, status, delete."""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_owned_issue
from app.database import get_db
from app.models import Issue, Project, User
from app.schemas.enums import Priority, Status
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate

router = APIRouter(prefix="/issues", tags=["issues"])
logger = logging.getLogger("issuetracker")

def _validate_assignee(db: Session, assignee_id: Optional[int]) -> None:
    if assignee_id is not None and db.get(User, assignee_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee not found")

@router.get("", response_model=list[IssueResponse])
def list_issues(search: Optional[str] = None, status_filter: Optional[Status] = None, priority: Optional[Priority] = None, assignee_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Issue]:
    stmt = select(Issue).join(Project, Issue.project_id == Project.id).where(Project.owner_id == current_user.id)
    if search: stmt = stmt.where(Issue.title.ilike(f"%{search}%"))
    if status_filter is not None: stmt = stmt.where(Issue.status == status_filter.value)
    if priority is not None: stmt = stmt.where(Issue.priority == priority.value)
    if assignee_id is not None: stmt = stmt.where(Issue.assignee_id == assignee_id)
    return list(db.scalars(stmt).all())

@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(payload: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Issue:
    project = db.get(Project, payload.project_id)
    if project is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user.id: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add issues to this project")
    _validate_assignee(db, payload.assignee_id)
    issue = Issue(title=payload.title, description=payload.description, priority=payload.priority.value, status=payload.status.value, project_id=payload.project_id, assignee_id=payload.assignee_id)
    db.add(issue); db.commit(); db.refresh(issue)
    logger.info("issue created: id=%s project=%s", issue.id, project.id)
    return issue

@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(issue: Issue = Depends(get_owned_issue)) -> Issue:
    return issue

@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(payload: IssueUpdate, issue: Issue = Depends(get_owned_issue), db: Session = Depends(get_db)) -> Issue:
    data = payload.model_dump(exclude_unset=True)
    if "assignee_id" in data: _validate_assignee(db, data["assignee_id"])
    if isinstance(data.get("priority"), Priority): data["priority"] = data["priority"].value
    if isinstance(data.get("status"), Status): data["status"] = data["status"].value
    for field, value in data.items(): setattr(issue, field, value)
    issue.updated_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(issue)
    logger.info("issue updated: id=%s fields=%s", issue.id, list(data.keys()))
    return issue

@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue: Issue = Depends(get_owned_issue), db: Session = Depends(get_db)) -> None:
    db.delete(issue); db.commit(); logger.info("issue deleted: id=%s", issue.id)
