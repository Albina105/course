from fastapi import FastAPI
from mysite.admin.setup import setup_admin
from mysite.api import users, category, course, studygroup, application, enrollment, ai
from mysite.database.db import engine, Base
from mysite.database import models
import uvicorn

Base.metadata.create_all(bind=engine)

edu_app = FastAPI()

edu_app.include_router(category.category_router)
edu_app.include_router(course.course_router)
edu_app.include_router(studygroup.group_router)
edu_app.include_router(application.application_router)
edu_app.include_router(enrollment.enrollment_router)
edu_app.include_router(users.user_router)
edu_app.include_router(ai.ai_router)
setup_admin(edu_app)


if __name__ == '__main__':
    uvicorn.run(edu_app, host="127.0.0.1", port=8000)
