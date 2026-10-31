from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.api.users import get_student
from mysite.database.db import SessionLocal
from mysite.database.models import Enrollment, StudyGroup, User, GroupStatus, EnrollmentStatus
from mysite.schemas.enrollment_schema import EnrollmentCreateSchema, EnrollmentUpdateSchema, EnrollmentOutSchema

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


enrollment_router = APIRouter(prefix='/enrollments', tags=['Enrollment'])

def get_queryset(db: Session, student: User):
    return db.query(Enrollment).filter(Enrollment.student_id == student.id)

@enrollment_router.post('/', response_model=EnrollmentOutSchema)
async def create_enrollment(enrollment: EnrollmentCreateSchema, db: Session = Depends(get_db),
                            student: User = Depends(get_student)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == enrollment.group_id).first()
    if not group_db:
        raise HTTPException(detail='Group not found', status_code=404)
    if group_db.status != GroupStatus.recruiting:
        raise HTTPException(detail='Группа не набирает студентов!', status_code=400)
    active_count = db.query(Enrollment).filter(Enrollment.group_id == group_db.id,
                                               Enrollment.status == EnrollmentStatus.active).count()
    if active_count >= group_db.capacity:
        raise HTTPException(detail='Группа заполнена!', status_code=400)
    enrollment_db = Enrollment(student_id=student.id, group_id=group_db.id)
    db.add(enrollment_db)
    db.commit()
    db.refresh(enrollment_db)
    return enrollment_db

@enrollment_router.get('/', response_model=List[EnrollmentOutSchema])
async def list_enrollments(db: Session = Depends(get_db), student: User = Depends(get_student)):
    return get_queryset(db, student).all()

@enrollment_router.get('/{enrollment_id}', response_model=EnrollmentOutSchema)
async def get_enrollment(enrollment_id: int, db: Session = Depends(get_db),
                         student: User = Depends(get_student)):
    enrollment_db = get_queryset(db, student).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(detail='Enrollment not found', status_code=404)
    return enrollment_db

@enrollment_router.put('/{enrollment_id}', response_model=dict)
async def update_enrollment(enrollment_id: int, enrollment: EnrollmentUpdateSchema,
                            db: Session = Depends(get_db), student: User = Depends(get_student)):
    enrollment_db = get_queryset(db, student).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(detail='Enrollment not found', status_code=404)
    for enrollment_key, enrollment_value in enrollment.dict().items():
        setattr(enrollment_db, enrollment_key, enrollment_value)
    db.commit()
    db.refresh(enrollment_db)
    return {'message': 'Enrollment была успешно изменена!'}

@enrollment_router.delete('/{enrollment_id}', response_model=dict)
async def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db),
                            student: User = Depends(get_student)):
    enrollment_db = get_queryset(db, student).filter(Enrollment.id == enrollment_id).first()
    if not enrollment_db:
        raise HTTPException(detail='Enrollment not found', status_code=404)
    db.delete(enrollment_db)
    db.commit()
    return {'message': 'Enrollment была успешно удалена!'}
