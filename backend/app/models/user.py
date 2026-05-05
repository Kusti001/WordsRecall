from datetime import date, datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)

    new_words_limit: Mapped[int] = mapped_column(default=5, server_default="5")
    new_words_added_today: Mapped[int] = mapped_column(default=0, server_default="0")
    last_new_words_date: Mapped[date | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime | None] = mapped_column(server_default=func.now())
    
    user_words: Mapped[list["UserWord"]] = relationship(back_populates="user", cascade="all, delete-orphan")
