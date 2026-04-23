from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import func, ForeignKey
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

new_session = async_sessionmaker(engine, expire_on_commit=False)

class Model(DeclarativeBase):
    pass

class User(Model):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    user_words: Mapped[list["UserWord"]] = relationship(back_populates="user")

class Word(Model):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(unique=True)
    level: Mapped[str | None]
    meaning: Mapped[str | None]
    example: Mapped[str | None]
    translation: Mapped[str]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_words: Mapped[list["UserWord"]] = relationship(back_populates="word")

class UserWord(Model):
    __tablename__ = "user_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    
    interval: Mapped[int] = mapped_column(default=1) # Интервал между повторениями в днях
    repetitions: Mapped[int] = mapped_column(default=0) # Правильные ответы подряд
    next_review: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="user_words")
    word: Mapped["Word"] = relationship(back_populates="user_words")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user_word")

class Review(Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_word_id: Mapped[int] = mapped_column(ForeignKey("user_words.id"))
    result: Mapped[str]
    reviewed_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_word: Mapped["UserWord"] = relationship(back_populates="reviews")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)