from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .core.database import engine, Base, get_db
from .models.user import User
from .schemas.user import UserCreate, UserRead

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте (только для разработки!)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Language Bot API", version="0.1", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Language Bot API работает!"}

@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(telegram_id=user.telegram_id, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user