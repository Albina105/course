from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'sqlite:///./education.db'
engine = create_engine(DB_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
