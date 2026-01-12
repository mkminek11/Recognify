
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin, current_user
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, Text, Float

import os.path
import datetime
import werkzeug.security

from app.app import db, app, decode, encode, encode_image, login


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

    def is_admin(self) -> bool:
        return self.permission >= 10

    def hid(self) -> str:
        return encode(self.id)
    
    def data(self) -> dict:
        return {
            "id": self.hid(),
            "username": self.username,
            "email": self.email,
        }

    def has_access_to(self, draft: "Draft | int | str | None") -> bool:
        if isinstance(draft, str):
            draft = decode(draft)
        if isinstance(draft, int):
            draft = Draft.query.get(draft)
        if draft is None or not isinstance(draft, Draft): return False
        if draft.owner_id == self.id: return True
        return any(access.user_id == self.id for access in draft.access_users)

    def avatar_url(self, size: int = 128) -> str:
        import hashlib
        email = self.email.lower().encode('utf-8') if self.email else b""
        hash_email = hashlib.md5(email).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_email}?d=identicon&s={size}"
    

class Set(db.Model):
    __tablename__ = "sets"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    name: Mapped[str] = mapped_column(String(64), unique = True, nullable = False)
    description: Mapped[str] = mapped_column(Text, default = "", nullable = False)
    is_public: Mapped[bool] = mapped_column(Boolean, default = False, nullable = False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default = datetime.datetime.utcnow, nullable = False)
    # TODO: modified_at
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

    def hid(self) -> str:
        return encode(self.id)
    
    def data(self) -> dict:
        return {
            "id": self.hid(),
            "name": self.name,
            "description": self.description,
            "owner_id": encode(self.owner_id),
            "created_at": self.created_at.isoformat(),
            "is_public": self.is_public
        }

    def get_draft(self) -> "Draft | None":
        return db.session.execute(Draft.query.where(Draft.set_id == self.id)).scalar_one_or_none()

    def skip_images(self, user_id: int) -> list[str]:
        res = db.session.execute(SkipImage.query.join(Image).where(Image.set_id == self.id, SkipImage.user_id == user_id)).scalars().all()
        return [skip.hid() for skip in res if isinstance(skip, SkipImage)]


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    filename: Mapped[str] = mapped_column(String(128), nullable = False)
    set_id: Mapped[int] = mapped_column(ForeignKey("sets.id"), nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = True)
    draft_image_id: Mapped[int | None] = mapped_column(ForeignKey("draft_images.id"), nullable = True, default = None)

    set: Mapped["Set"] = relationship("Set", back_populates = "images", lazy = "select")
    draft_image: Mapped["DraftImage | None"] = relationship("DraftImage", lazy = "select")

    def __init__(self, filename: str, label: str = "", set_id: int = 0, draft_image_id: int | None = None):
        self.filename = filename
        self.label = label
        self.set_id = set_id
        self.draft_image_id = draft_image_id

    def hid(self) -> str:
        return encode_image(self.set_id, self.id)
    
    def data(self) -> dict:
        return {
            "id": self.hid(),
            "filename": self.filename,
            "label": self.label,
            "set_id": encode(self.set_id)
        }

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
    access_users: Mapped[list["DraftAccess"]] = relationship("DraftAccess", back_populates = "draft", lazy = "select", cascade = "all, delete-orphan")

    def __init__(self):
        self.owner_id = current_user.id if current_user and current_user.is_authenticated else 0

    def hid(self) -> str:
        return encode(self.id)
    
    def data(self) -> dict:
        return {
            "id": self.hid(),
            "name": self.name,
            "description": self.description,
            "owner_id": encode(self.owner_id),
            "created_at": self.created_at.isoformat(),
            "set_id": encode(self.set_id) if self.set_id else None
        }

    def get_access_users(self) -> list[User]:
        return [user for access in self.access_users if (user := access.user)]


class DraftImage(db.Model):
    __tablename__ = "draft_images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"), nullable = False)
    filename: Mapped[str] = mapped_column(String(128), nullable = False)
    slide: Mapped[int] = mapped_column(Integer, nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = True)

    draft: Mapped["Draft"] = relationship("Draft", back_populates = "images")

    def __init__(self, draft_id: int, filename: str, presentation_n: int, slide_n: int, label: str = ""):
        self.draft_id = draft_id
        self.filename = filename
        self.slide = presentation_n * 10_000 + slide_n
        self.label = label

    def hid(self) -> str:
        return encode_image(self.draft_id, self.id)
    
    def data(self) -> dict:
        return {
            "id": self.hid(),
            "filename": self.filename,
            "label": self.label,
            "slide": self.slide,
            "draft_id": encode(self.draft_id)
        }


class DraftLabel(db.Model):
    __tablename__ = "draft_labels"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"), nullable = False)
    label: Mapped[str] = mapped_column(String(128), nullable = False)
    slide: Mapped[int] = mapped_column(Integer, nullable = False)

    draft: Mapped["Draft"] = relationship("Draft", back_populates = "labels")

    def __init__(self, draft_id: int, label: str, presentation_n: int, slide_n: int):
        self.draft_id = draft_id
        self.label = label
        self.slide = presentation_n * 10_000 + slide_n

    def hid(self) -> str:
        return encode_image(self.draft_id, self.id)

    def data(self) -> dict:
        return {
            "id": self.hid(),
            "label": self.label,
            "slide": self.slide,
            "draft_id": encode(self.draft_id)
        }


class SkipImage(db.Model):
    __tablename__ = "skip_images"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id"), nullable = False)

    def __init__(self, user_id: int, image_id: int):
        self.user_id = user_id
        self.image_id = image_id

    def hid(self) -> str:
        img = Image.query.where(Image.id == self.image_id).first()
        if not isinstance(img, Image): return ""
        return encode_image(img.set_id, self.id)

    def data(self) -> dict:
        return {
            "user_id": encode(self.user_id),
            "image_id": encode_image(0, self.image_id)  # set_id is not known here
        }


class DraftAccess(db.Model):
    __tablename__ = "draft_access"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("drafts.id"), nullable = False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)

    user: Mapped["User"] = relationship("User", lazy = "select")
    draft: Mapped["Draft"] = relationship("Draft", back_populates = "access_users", lazy = "select")

    def __init__(self, draft_id: int, user_id: int):
        self.draft_id = draft_id
        self.user_id = user_id
