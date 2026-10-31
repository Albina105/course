from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.api.users import get_student, get_manager
from mysite.database.db import SessionLocal
from mysite.database.models import Application, Course, User, UserStatus, CourseStatus
from mysite.schemas.application_schema import ApplicationCreateSchema, ApplicationUpdateSchema, ApplicationOutSchema

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


application_router = APIRouter(prefix='/applications', tags=['Application'])

@application_router.post('/', response_model=ApplicationOutSchema)
async def create_application(application: ApplicationCreateSchema, db: Session = Depends(get_db),
                             student: User = Depends(get_student)):
    course_db = db.query(Course).filter(Course.id == application.course_id).first()
    if not course_db:
        raise HTTPException(detail='Course not found', status_code=404)
    if student.user_status == UserStatus.free and course_db.status != CourseStatus.free:
        raise HTTPException(detail='Для этого курса нужен pro статус!', status_code=403)
    application_db = Application(student_id=student.id, course_id=application.course_id,
                                 comment=application.comment)
    db.add(application_db)
    db.commit()
    db.refresh(application_db)
    return application_db

@application_router.get('/', response_model=List[ApplicationOutSchema])
async def list_applications(db: Session = Depends(get_db), manager: User = Depends(get_manager)):
    return db.query(Application).all()

@application_router.get('/{application_id}', response_model=ApplicationOutSchema)
async def get_application(application_id: int, db: Session = Depends(get_db),
                          manager: User = Depends(get_manager)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(detail='Application not found', status_code=404)
    return application_db

@application_router.put('/{application_id}', response_model=dict)
async def update_application(application_id: int, application: ApplicationUpdateSchema,
                             db: Session = Depends(get_db), manager: User = Depends(get_manager)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(detail='Application not found', status_code=404)
    for application_key, application_value in application.dict().items():
        setattr(application_db, application_key, application_value)
    application_db.manager_id = manager.id
    db.commit()
    db.refresh(application_db)
    return {'message': 'Application была успешно изменена!'}

@application_router.delete('/{application_id}', response_model=dict)
async def delete_application(application_id: int, db: Session = Depends(get_db),
                             manager: User = Depends(get_manager)):
    application_db = db.query(Application).filter(Application.id == application_id).first()
    if not application_db:
        raise HTTPException(detail='Application not found', status_code=404)
    db.delete(application_db)
    db.commit()
    return {'message': 'Application была успешно удалена!'}
