
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin, current_user
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Text, Float

import os.path
import datetime
import werkzeug.security

from app.app import db, app, login, hid


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    username: Mapped[str] = mapped_column(String(32), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(120), unique = True, nullable = True)
    password: Mapped[str] = mapped_column(String(64), nullable = False)
    permission: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)

    sets: Mapped[list["Set"]] = relationship("Set", back_populates = "owner", lazy = "select")

    def __init__(self, username: str, email: str, password: str, permission: int = 0):
        for attr, value in locals().items():
            if attr == 'self': continue
            setattr(self, attr, value)

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

    owner: Mapped["User"] = relationship("User", back_populates = "sets", lazy = "select")
    images: Mapped[list["Image"]] = relationship("Image", back_populates = "set", lazy = "select")

    @staticmethod
    def all() -> list["Set"]: return Set.query.all()

    def __init__(self, name: str, description: str = "", is_public: bool = False):
        self.name = name
        self.description = description
        self.is_public = is_public
        self.owner_id = current_user.id if current_user and current_user.is_authenticated else 0


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    filename: Mapped[str] = mapped_column(String(128), nullable = False)
    set_id: Mapped[int] = mapped_column(ForeignKey("sets.id"), nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = True)

    set: Mapped["Set"] = relationship("Set", back_populates = "images", lazy = "select")

    def __init__(self, filename: str, label: str = "", set_id: int = 0):
        self.filename = filename
        self.label = label
        self.set_id = set_id


class Draft(db.Model):
    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(64), nullable = False, default = "")
    description: Mapped[str] = mapped_column(Text, default = "", nullable = False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)
    presentations: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)
    set_id: Mapped[int | None] = mapped_column(ForeignKey("sets.id"), nullable = True, default = None)

    images: Mapped[list["DraftImage"]] = relationship("DraftImage", back_populates = "draft", lazy = "select", cascade = "all, delete-orphan")
    labels: Mapped[list["DraftLabel"]] = relationship("DraftLabel", back_populates = "draft", lazy = "select", cascade = "all, delete-orphan")
    owner: Mapped["User"] = relationship("User", lazy = "select")
    set: Mapped["Set | None"] = relationship("Set", lazy = "select")

    def __init__(self):
        self.owner_id = current_user.id if current_user and current_user.is_authenticated else 0

    def hash(self) -> str: return hid.encode(self.id)


class DraftImage(db.Model):
    __tablename__ = "draft_images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"), nullable = False)
    filename: Mapped[str] = mapped_column(String(128), nullable = False)
    slide: Mapped[int] = mapped_column(Integer, nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = True)

    draft: Mapped["Draft"] = relationship("Draft", back_populates = "images")

    def __init__(self, draft_id: int, filename: str, presentation_n: int, slide_n: int, label: str = ""):
        slide = presentation_n * 10_000 + slide_n
        for attr, value in locals().items():
            setattr(self, attr, value)


class DraftLabel(db.Model):
    __tablename__ = "draft_labels"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"), nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = False)
    slide: Mapped[int] = mapped_column(Integer, nullable = False)

    draft: Mapped["Draft"] = relationship("Draft", back_populates = "labels")

    def __init__(self, draft_id: int, label: str, presentation_n: int, slide_n: int):
        slide = presentation_n * 10_000 + slide_n
        for attr, value in locals().items():
            setattr(self, attr, value)
