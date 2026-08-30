from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_projects: int
    total_issues: int
    open_issues: int
    completed_issues: int
