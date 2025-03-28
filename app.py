
from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, current_user
from typing import Callable



app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "My Very Secret Key 1234"


class Base(DeclarativeBase): pass

db = SQLAlchemy(model_class = Base)
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)


def login_required(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and current_user.verified:
            return func(*args, **kwargs)

        return redirect(url_for("index", next = request.path.lstrip("/")))
    
    wrapper.__name__ = func.__name__
    return wrapper


def permission_required(permission: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if current_user.permission >= permission:
                return func(*args, **kwargs)

            return redirect(url_for("index", next = request.path.lstrip("/")))
        
        wrapper.__name__ = func.__name__
        return wrapper
    
    return decorator


__all__ = [
    "app",
    "db",
    "login_manager",
    "login_required",
    "permission_required"
]
