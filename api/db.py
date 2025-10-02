from api.lib import *

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
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

    def authenticate(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

with app.app_context():
    db.create_all()

ROOT_PATH = app.root_path
UPLOAD_PATH = os.path.join(ROOT_PATH, "static", "uploads")

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()
