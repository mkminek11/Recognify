from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "My Very Secret Key 1234"


class Base(DeclarativeBase): pass

db = SQLAlchemy(model_class = Base)
db.init_app(app)



class Presentation(db.Model):
    # __tablename__ = "presentation"

    id:    Mapped[int] = mapped_column(db.Integer, primary_key = True)
    uuid:  Mapped[str] = mapped_column(db.String(36), nullable = False)
    title: Mapped[str] = mapped_column(db.String(100), nullable = False)

    def __repr__(self):
        return f"<Presentation {self.id}>"


class Image(db.Model):
    # __tablename__ = "image"

    id:           Mapped[int] = mapped_column(db.Integer, primary_key = True)
    file:         Mapped[str] = mapped_column(db.Integer, nullable = False)
    presentation: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("presentation.id"), nullable = False)
    slide:        Mapped[int] = mapped_column(db.Integer, nullable = False)
    title:        Mapped[str] = mapped_column(db.String(100), nullable = False)

    def __repr__(self):
        return f"<Image {self.id}>"
    

class Label(db.Model):
    # __tablename__ = "label"

    id:           Mapped[int] = mapped_column(db.Integer, primary_key = True)
    text:         Mapped[str] = mapped_column(db.String(100), nullable = False)
    presentation: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("presentation.id"), nullable = False)
    slide:        Mapped[int] = mapped_column(db.Integer, nullable = False)

    def __repr__(self):
        return f"<Label {self.id}>"
    

with app.app_context():
    db.create_all()