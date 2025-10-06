
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Text, Float

import os.path
import datetime
import werkzeug.security

from app.app import db, app, login


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    username: Mapped[str] = mapped_column(String(32), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(64), nullable = False)
    permission: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)

    sets: Mapped[list["Set"]] = relationship("Set", back_populates = "owner", lazy = "joined")

    def authenticate(self, password: str) -> bool:
        return werkzeug.security.check_password_hash(self.password, password)
    

class Set(db.Model):
    __tablename__ = "sets"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(64), unique = True, nullable = False)
    description: Mapped[str] = mapped_column(Text, default = "", nullable = False)
    is_public: Mapped[bool] = mapped_column(Boolean, default = False, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)

    owner: Mapped["User"] = relationship("User", back_populates = "sets", lazy = "joined")
    images: Mapped[list["Image"]] = relationship("Image", back_populates = "set", lazy = "joined")

    @staticmethod
    def all() -> list["Set"]: return Set.query.all()


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    filename: Mapped[str] = mapped_column(String(128), unique = True, nullable = False)
    original_filename: Mapped[str] = mapped_column(String(128), nullable = False)
    set_id: Mapped[int] = mapped_column(ForeignKey("sets.id"), nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = True)

    set: Mapped["Set"] = relationship("Set", back_populates = "images", lazy = "joined")

