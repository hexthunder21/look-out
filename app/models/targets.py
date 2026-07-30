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
    target_url: Mapped[str] = mapped_column(String(255))
    owner: Mapped[User] = relationship(back_populates="targets", lazy="joined")