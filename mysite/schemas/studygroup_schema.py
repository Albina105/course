from pydantic import BaseModel
from datetime import date, datetime
from mysite.database.models import GroupStatus


class StudyGroupInputSchema(BaseModel):
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: date
    capacity: int
    status: GroupStatus = GroupStatus.recruiting

class StudyGroupOutSchema(BaseModel):
    id: int
    name: str
    course_id: int
    teacher_id: int
    starts_on: date
    ends_on: date
    capacity: int
    status: GroupStatus
    created_at: datetime
    updated_at: datetime
