from pydantic import BaseModel
from datetime import datetime
from mysite.database.models import EnrollmentStatus


class EnrollmentCreateSchema(BaseModel):
    group_id: int

class EnrollmentUpdateSchema(BaseModel):
    status: EnrollmentStatus

class EnrollmentOutSchema(BaseModel):
    id: int
    student_id: int
    group_id: int
    status: EnrollmentStatus
    created_at: datetime
