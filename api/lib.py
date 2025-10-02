# import functools
from functools import wraps
import re
from typing import Callable
from flask import Flask, redirect, render_template, url_for, request, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = ""


login_manager = LoginManager()
login_manager.init_app(app)


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

@app.template_filter("regex_replace")
def regex_replace(string: str, find: str, replace: str) -> str:
    return re.sub(find, replace, string)

@app.template_filter("format_number")
def format_number(value: int | float) -> str:
    if not isinstance(value, (int, float)): value = float(value)

    if value < 1_000:
        return str(value)
    elif value < 1_000_000:
        return f"{value / 1_000:.0f} K"
    else:
        return f"{value / 1_000_000:.0f} M"
