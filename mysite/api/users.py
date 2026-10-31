from fastapi import APIRouter, HTTPException, Depends
from mysite.database.db import SessionLocal
from mysite.database.models import User, RefreshToken, UserRole
from mysite.schemas.auth_schema import UserInputSchema, UserLoginSchema
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from mysite.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME
from datetime import timedelta, datetime
from jose import jwt, JWTError
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

user_router = APIRouter(prefix="/users", tags=["User"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
    except JWTError:
        raise HTTPException(detail='Токен неверный!', status_code=401)
    user_db = db.query(User).filter(User.email == email).first()
    if not user_db:
        raise HTTPException(detail='Пользователь не найден!', status_code=401)
    return user_db

async def get_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(detail='Нет доступа!', status_code=403)
    return current_user

async def get_teacher(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.teacher:
        raise HTTPException(detail='Нет доступа!', status_code=403)
    return current_user

async def get_manager(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.manager:
        raise HTTPException(detail='Нет доступа!', status_code=403)
    return current_user

async def get_student(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.student:
        raise HTTPException(detail='Нет доступа!', status_code=403)
    return current_user


@user_router.post('/register', response_model=dict)
async def register(user: UserInputSchema, db: Session = Depends(get_db)):
    email_db = db.query(User).filter(User.email == user.email).first()
    if email_db:
        raise HTTPException(detail='Такой email уже есть!', status_code=400)

    hash_password = get_password_hash(user.password)
    user_data = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password,
        role=user.role,
        user_status=user.user_status,
    )
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {'message': 'Регистрация прошла успешно!'}


@user_router.post('/login/', response_model=dict)
async def login(user: UserLoginSchema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db or not verify_password(user.password, user_db.password):
        raise HTTPException(detail='Неверные данные!', status_code=400)

    access_token = create_access_token({'sub': user_db.email})
    refresh_token = create_refresh_token({'sub': user_db.email})

    token_db = RefreshToken(user_id=user_db.id, token=refresh_token)
    db.add(token_db)
    db.commit()

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}


@user_router.post('/logout/', response_model=dict)
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Токен неверный!')
    db.delete(stored_token)
    db.commit()
    return {'message': 'Вышли!'}


@user_router.post('/refresh/', response_model=dict)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Токен неверный!')
    access_token = create_access_token({'sub': stored_token.token_user.email})
    return {'access_token': access_token, 'token_type': 'Bearer'}
