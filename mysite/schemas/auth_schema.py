from pydantic import BaseModel
from datetime import datetime
from mysite.database.models import UserRole, UserStatus


class UserInputSchema(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRole = UserRole.student
    user_status: UserStatus = UserStatus.free

class UserOutSchema(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    user_status: UserStatus
    created_at: datetime
    updated_at: datetime

class UserLoginSchema(BaseModel):
    email: str
    password: str
