from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.database.db import SessionLocal
from mysite.database.models import StudyGroup
from mysite.schemas.studygroup_schema import StudyGroupInputSchema, StudyGroupOutSchema

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


group_router = APIRouter(prefix='/groups', tags=['StudyGroup'])

@group_router.post('/', response_model=StudyGroupOutSchema)
async def create_group(group: StudyGroupInputSchema, db: Session = Depends(get_db)):
    group_db = StudyGroup(**group.dict())
    db.add(group_db)
    db.commit()
    db.refresh(group_db)
    return group_db

@group_router.get('/', response_model=List[StudyGroupOutSchema])
async def list_groups(db: Session = Depends(get_db)):
    return db.query(StudyGroup).all()

@group_router.get('/{group_id}', response_model=StudyGroupOutSchema)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail='StudyGroup not found', status_code=404)
    return group_db

@group_router.put('/{group_id}', response_model=dict)
async def update_group(group_id: int, group: StudyGroupInputSchema, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail='StudyGroup not found', status_code=404)
    for group_key, group_value in group.dict().items():
        setattr(group_db, group_key, group_value)
    db.commit()
    db.refresh(group_db)
    return {'message': 'StudyGroup была успешно изменена!'}

@group_router.delete('/{group_id}', response_model=dict)
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    group_db = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group_db:
        raise HTTPException(detail='StudyGroup not found', status_code=404)
    db.delete(group_db)
    db.commit()
    return {'message': 'StudyGroup была успешно удалена!'}
