from .views import UserAdmin, RefreshTokenAdmin, CategoryAdmin, CourseAdmin, StudyGroupAdmin, ApplicationAdmin, EnrollmentAdmin

from fastapi import FastAPI
from sqladmin import Admin
from mysite.database.db import engine


def setup_admin(edu_app: FastAPI):
    admin = Admin(edu_app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(RefreshTokenAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(StudyGroupAdmin)
    admin.add_view(ApplicationAdmin)
    admin.add_view(EnrollmentAdmin)
