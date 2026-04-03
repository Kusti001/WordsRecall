from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)  # echo=True — видит SQL в консоли
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()