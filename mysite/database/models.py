from .db import Base
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, Enum, Date, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, date
from typing import Optional, List
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    student = 'student'
    teacher = 'teacher'
    manager = 'manager'
    admin = 'admin'


class UserStatus(str, PyEnum):
    free = 'free'
    pro = 'pro'


class CourseLevel(str, PyEnum):
    beginner = 'beginner'
    intermediate = 'intermediate'
    advanced = 'advanced'


class CourseStatus(str, PyEnum):
    free = 'free'
    plus = 'plus'


class GroupStatus(str, PyEnum):
    recruiting = 'recruiting'
    active = 'active'
    completed = 'completed'
    cancelled = 'cancelled'


class ApplicationStatus(str, PyEnum):
    new = 'new'
    in_progress = 'in_progress'
    accepted = 'accepted'
    rejected = 'rejected'
    cancelled = 'cancelled'


class EnrollmentStatus(str, PyEnum):
    active = 'active'
    completed = 'completed'
    cancelled = 'cancelled'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(64))
    email: Mapped[str] = mapped_column(String(64), unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student)
    user_status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.free)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    teacher_groups: Mapped[List['StudyGroup']] = relationship(back_populates='teacher')
    student_applications: Mapped[List['Application']] = relationship(foreign_keys='Application.student_id',
                                                                     back_populates='student',
                                                                     cascade='all, delete-orphan')
    manager_applications: Mapped[List['Application']] = relationship(foreign_keys='Application.manager_id',
                                                                     back_populates='manager')
    student_enrollments: Mapped[List['Enrollment']] = relationship(back_populates='student',
                                                                   cascade='all, delete-orphan')
    user_token: Mapped[List['RefreshToken']] = relationship(back_populates='token_user',
                                                            cascade='all, delete-orphan')

    def __str__(self):
        return self.full_name


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    token_user: Mapped[User] = relationship(back_populates='user_token')
    token: Mapped[str] = mapped_column(String(512), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __str__(self):
        return f'{self.token_user}, {self.token}'


class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(32), unique=True)
    category_courses: Mapped[List['Course']] = relationship(back_populates='category',
                                                            cascade='all, delete-orphan')

    def __str__(self):
        return self.category_name


class Course(Base):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column(String(64))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    category: Mapped[Category] = relationship(back_populates='category_courses')
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel), default=CourseLevel.beginner)
    price: Mapped[int] = mapped_column(Integer)
    duration_weeks: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus), default=CourseStatus.free)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    course_groups: Mapped[List['StudyGroup']] = relationship(back_populates='course',
                                                             cascade='all, delete-orphan')
    course_applications: Mapped[List['Application']] = relationship(back_populates='course',
                                                                    cascade='all, delete-orphan')

    def __str__(self):
        return self.title


class StudyGroup(Base):
    __tablename__ = 'study_group'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped[Course] = relationship(back_populates='course_groups')
    teacher_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    teacher: Mapped[User] = relationship(back_populates='teacher_groups')
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    capacity: Mapped[int] = mapped_column(Integer, default=20, server_default='20')
    status: Mapped[GroupStatus] = mapped_column(Enum(GroupStatus), default=GroupStatus.recruiting)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    group_enrollments: Mapped[List['Enrollment']] = relationship(back_populates='group',
                                                                 cascade='all, delete-orphan')

    def __str__(self):
        return self.name


class Application(Base):
    __tablename__ = 'application'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student: Mapped[User] = relationship(foreign_keys=[student_id], back_populates='student_applications')
    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'))
    course: Mapped[Course] = relationship(back_populates='course_applications')
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'), nullable=True)
    manager: Mapped[Optional[User]] = relationship(foreign_keys=[manager_id], back_populates='manager_applications')
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.new)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return f'{self.student}, {self.course}, {self.status}'


class Enrollment(Base):
    __tablename__ = 'enrollment'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    student: Mapped[User] = relationship(back_populates='student_enrollments')
    group_id: Mapped[int] = mapped_column(ForeignKey('study_group.id'))
    group: Mapped[StudyGroup] = relationship(back_populates='group_enrollments')
    status: Mapped[EnrollmentStatus] = mapped_column(Enum(EnrollmentStatus), default=EnrollmentStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __str__(self):
        return f'{self.student}, {self.group}, {self.status}'
