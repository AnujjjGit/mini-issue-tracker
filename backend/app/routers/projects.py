"""Project endpoints: create, list, view, edit, archive."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_owned_project
from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])
logger = logging.getLogger("issuetracker")

def _ensure_unique_name(db: Session, owner_id: int, name: str, exclude_id: Optional[int] = None):
    stmt = select(Project).where(Project.owner_id == owner_id, Project.name == name)
    if exclude_id is not None: stmt = stmt.where(Project.id != exclude_id)
    if db.scalar(stmt) is not None: raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project name already exists")

@router.get("", response_model=list[ProjectResponse])
def list_projects(include_archived: bool = False, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Project]:
    stmt = select(Project).where(Project.owner_id == current_user.id)
    if not include_archived: stmt = stmt.where(Project.archived.is_(False))
    return list(db.scalars(stmt).all())

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Project:
    _ensure_unique_name(db, current_user.id, payload.name)
    project = Project(name=payload.name, description=payload.description, owner_id=current_user.id)
    db.add(project); db.commit(); db.refresh(project)
    logger.info("project created: id=%s owner=%s", project.id, current_user.id)
    return project

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project: Project = Depends(get_owned_project)) -> Project:
    return project

@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(payload: ProjectUpdate, project: Project = Depends(get_owned_project), db: Session = Depends(get_db)) -> Project:
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] != project.name: _ensure_unique_name(db, project.owner_id, data["name"], exclude_id=project.id)
    for field, value in data.items(): setattr(project, field, value)
    db.commit(); db.refresh(project); logger.info("project updated: id=%s", project.id)
    return project

@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(project: Project = Depends(get_owned_project), db: Session = Depends(get_db)) -> Project:
    project.archived = True
    db.commit(); db.refresh(project); logger.info("project archived: id=%s", project.id)
    return project
