from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Null, String, ForeignKey
from app import app, db, login_manager
from flask_login import UserMixin
from hashlib import sha256



class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id:         Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    uuid:       Mapped[str] = mapped_column(String,  unique = True, nullable = False, default = lambda: uuid4().hex)
    email:      Mapped[str] = mapped_column(String,  unique = True, nullable = False)
    fname:      Mapped[str] = mapped_column(String,  nullable = False)
    lname:      Mapped[str] = mapped_column(String,  nullable = False)
    password:   Mapped[str] = mapped_column(String,  nullable = False)
    permission: Mapped[int] = mapped_column(Integer, nullable = False, default = 0)

    def check_password(self, password: str) -> bool:
        return self.password == sha256(password.encode("utf-8")).hexdigest()
    
    def get_full_name(self) -> str:
        return f"{self.fname} {self.lname}"


class Presentation(db.Model):
    __tablename__ = "presentation"

    id:    Mapped[int] = mapped_column(Integer, primary_key = True)
    uuid:  Mapped[str] = mapped_column(String(36), nullable = False, unique = True, default = lambda: uuid4().hex)
    title: Mapped[str] = mapped_column(String(100), nullable = False)

    images = db.relationship("Image", back_populates = "presentation")
    labels = db.relationship("Label", back_populates = "presentation")

    def __repr__(self):
        return f"<Presentation {self.id}>"


class Image(db.Model):
    __tablename__ = "image"

    id:      Mapped[int] = mapped_column(Integer, primary_key = True)
    file:    Mapped[str] = mapped_column(Integer, nullable = False)
    pres_id: Mapped[int] = mapped_column(Integer, ForeignKey("presentation.id"), nullable = False)
    slide:   Mapped[int] = mapped_column(Integer, nullable = False)
    title:   Mapped[str] = mapped_column(String(100), nullable = True, default = Null)

    presentation = db.relationship("Presentation", back_populates = "images")

    def __repr__(self):
        return f"<Image {self.id}>"
    

class Label(db.Model):
    __tablename__ = "label"

    id:      Mapped[int] = mapped_column(Integer, primary_key = True)
    text:    Mapped[str] = mapped_column(String(100), nullable = False)
    pres_id: Mapped[int] = mapped_column(Integer, ForeignKey("presentation.id"), nullable = False)
    slide:   Mapped[int] = mapped_column(Integer, nullable = False)

    presentation = db.relationship("Presentation", back_populates = "labels")

    def __repr__(self):
        return f"<Label {self.id}>"
    

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()


__all__ = [
    "User",
    "Presentation",
    "Image",
    "Label",
    "load_user"
]
