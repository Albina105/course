from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from mysite.database.models import ApplicationStatus


class ApplicationCreateSchema(BaseModel):
    course_id: int
    comment: Optional[str] = None

class ApplicationUpdateSchema(BaseModel):
    comment: Optional[str] = None
    status: ApplicationStatus

class ApplicationOutSchema(BaseModel):
    id: int
    student_id: int
    course_id: int
    manager_id: Optional[int] = None
    comment: Optional[str] = None
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
