from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.api.users import get_teacher
from mysite.database.db import SessionLocal
from mysite.database.models import Course
from mysite.schemas.course_schema import CourseInputSchema, CourseOutSchema

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


course_router = APIRouter(prefix='/courses', tags=['Course'], dependencies=[Depends(get_teacher)])

@course_router.post('/', response_model=CourseOutSchema)
async def create_course(course: CourseInputSchema, db: Session = Depends(get_db)):
    course_db = Course(**course.dict())
    db.add(course_db)
    db.commit()
    db.refresh(course_db)
    return course_db

@course_router.get('/', response_model=List[CourseOutSchema])
async def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()

@course_router.get('/{course_id}', response_model=CourseOutSchema)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(detail='Course not found', status_code=404)
    return course_db

@course_router.put('/{course_id}', response_model=dict)
async def update_course(course_id: int, course: CourseInputSchema, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(detail='Course not found', status_code=404)
    for course_key, course_value in course.dict().items():
        setattr(course_db, course_key, course_value)
    db.commit()
    db.refresh(course_db)
    return {'message': 'Course был успешно изменен!'}

@course_router.delete('/{course_id}', response_model=dict)
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    course_db = db.query(Course).filter(Course.id == course_id).first()
    if not course_db:
        raise HTTPException(detail='Course not found', status_code=404)
    db.delete(course_db)
    db.commit()
    return {'message': 'Course был успешно удален!'}
