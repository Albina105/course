from pydantic import BaseModel
from datetime import datetime
from mysite.database.models import CourseLevel, CourseStatus


class CourseInputSchema(BaseModel):
    title: str
    category_id: int
    description: str
    level: CourseLevel = CourseLevel.beginner
    price: int
    duration_weeks: int
    is_active: bool = True
    status: CourseStatus = CourseStatus.free

class CourseOutSchema(BaseModel):
    id: int
    title: str
    category_id: int
    description: str
    level: CourseLevel
    price: int
    duration_weeks: int
    is_active: bool
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
