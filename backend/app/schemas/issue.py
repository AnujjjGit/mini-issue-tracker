from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import Priority, Status


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    project_id: int
    assignee_id: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    assignee_id: Optional[int] = None


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    project_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime
