from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    platform: Mapped[str] = mapped_column(String(50))
    username: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    phone: Mapped[str] = mapped_column(String(length=15), nullable=True, default=None)
    target_url: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    owner: Mapped[User] = relationship(back_populates="targets", lazy="joined")