
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from functools import wraps
from flask_login import current_user
from typing import Callable
import os
import re


app = Flask(__name__, 
             instance_relative_config = True,
             template_folder = '../templates',
             static_folder = '../static')

class Base(DeclarativeBase): pass

login = LoginManager()
db = SQLAlchemy(model_class = Base)
migrate = Migrate(app, db)

os.makedirs(app.instance_path, exist_ok=True)

app.config.from_mapping(
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev"),
    DATABASE = os.path.join(app.instance_path, "db.sqlite"),
    SQLALCHEMY_DATABASE_URI = f"sqlite:///db.sqlite",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
)

ROOT_PATH = app.root_path
UPLOAD_PATH = os.path.join(ROOT_PATH, "static", "uploads")


def login_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(current_user.is_authenticated)
        if current_user.is_authenticated:
            return func(*args, **kwargs)

        return "Login required", 401
    return wrapper

def permission_required(permission: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.permission >= permission:
                return func(*args, **kwargs)

            return "Permission denied", 403
        return wrapper
    return decorator



@app.template_filter('regex_replace')
def regex_replace(string: str, find: str, replace: str) -> str:
    return re.sub(find, replace, string)

@app.template_filter('format_number')
def format_number(value: int | float) -> str:
    if not isinstance(value, (int, float)): value = float(value)

    if value < 1_000:
        return str(value)
    elif value < 1_000_000:
        return f"{value / 1_000:.0f} K"
    else:
        return f"{value / 1_000_000:.0f} M"
