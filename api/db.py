from lib import *

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from flask_login import UserMixin
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from flask_sqlalchemy import SQLAlchemy

import os.path
import datetime
from typing import Any, Literal
from hashlib import sha256
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from enum import Enum



class Base(DeclarativeBase): pass

db = SQLAlchemy(model_class = Base)
db.init_app(app)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    username: Mapped[str] = mapped_column(String(32), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(64), nullable = False)
    permission: Mapped[int] = mapped_column(Integer, default = 0, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)

    sets: Mapped[list["Set"]] = relationship("Set", back_populates = "owner", lazy = "joined")

    def authenticate(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()
    

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
    labels: Mapped[list["Label"]] = relationship("Label", back_populates = "set", lazy = "joined")

    @staticmethod
    def all() -> list["Set"]: return Set.query.all()


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    filename: Mapped[str] = mapped_column(String(128), unique = True, nullable = False)
    original_filename: Mapped[str] = mapped_column(String(128), nullable = False)
    set_id: Mapped[int] = mapped_column(ForeignKey("sets.id"), nullable = False)
    label_id: Mapped[int | None] = mapped_column(ForeignKey("labels.id"), nullable = True)

    set: Mapped["Set"] = relationship("Set", back_populates = "images", lazy = "joined")
    label: Mapped["Label | None"] = relationship("Label", back_populates = "images", lazy = "joined")


class Label(db.Model):
    __tablename__ = "labels"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(64), nullable = False)
    set_id: Mapped[int] = mapped_column(ForeignKey("sets.id"), nullable = False)

    set: Mapped["Set"] = relationship("Set", back_populates = "labels", lazy = "joined")
    images: Mapped[list["Image"]] = relationship("Image", back_populates = "label", lazy = "joined")


with app.app_context():
    db.create_all()

ROOT_PATH = app.root_path
UPLOAD_PATH = os.path.join(ROOT_PATH, "static", "uploads")

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()
