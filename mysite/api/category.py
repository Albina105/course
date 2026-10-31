from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from mysite.api.users import get_admin
from mysite.database.db import SessionLocal
from mysite.database.models import Category
from mysite.schemas.category_schema import CategoryInputSchema, CategoryOutSchema

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


category_router = APIRouter(prefix='/categories', tags=['Category'], dependencies=[Depends(get_admin)])

@category_router.post('/', response_model=CategoryOutSchema)
async def create_category(category: CategoryInputSchema, db: Session = Depends(get_db)):
    category_db = Category(**category.dict())
    db.add(category_db)
    db.commit()
    db.refresh(category_db)
    return category_db

@category_router.get('/', response_model=List[CategoryOutSchema])
async def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@category_router.get('/{category_id}', response_model=CategoryOutSchema)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(detail='Category not found', status_code=404)
    return category_db

@category_router.put('/{category_id}', response_model=dict)
async def update_category(category_id: int, category: CategoryInputSchema, db: Session = Depends(get_db)):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(detail='Category not found', status_code=404)
    for category_key, category_value in category.dict().items():
        setattr(category_db, category_key, category_value)
    db.commit()
    db.refresh(category_db)
    return {'message': 'Category была успешно изменена!'}

@category_router.delete('/{category_id}', response_model=dict)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category_db = db.query(Category).filter(Category.id == category_id).first()
    if not category_db:
        raise HTTPException(detail='Category not found', status_code=404)
    db.delete(category_db)
    db.commit()
    return {'message': 'Category была успешно удалена!'}
