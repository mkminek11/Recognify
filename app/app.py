
from flask import Flask, redirect, request, send_file
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from functools import wraps
from flask_login import current_user
from typing import Callable, Literal
from flask_cors import CORS
from io import BytesIO
import hashids
import os
import re
import requests


app = Flask(__name__, 
             instance_relative_config = True,
             template_folder = '../templates',
             static_folder = '../static')

CORS(app)

class Base(DeclarativeBase): pass

login = LoginManager()
db = SQLAlchemy(model_class = Base)

hid = hashids.Hashids(min_length = 8, salt = os.environ.get("HASHID_SALT", os.environ.get("HASHID_SALT", "dev")))

def decode(hashid: str) -> int | Literal[False]:
    decoded = hid.decode(hashid)
    if not decoded: return False
    if not isinstance(decoded[0], int): return False
    return decoded[0]

os.makedirs(app.instance_path, exist_ok=True)

app.config.from_mapping(
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev"),
    DATABASE = os.path.join(app.instance_path, "db.sqlite"),
    SQLALCHEMY_DATABASE_URI = f"sqlite:///db.sqlite",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    TEMPLATES_AUTO_RELOAD = True,
)

ROOT_PATH = os.path.split(app.root_path)[0]
UPLOAD_PATH = os.path.join(ROOT_PATH, "static", "uploads")
VALID_IMG_EXTENSIONS = ["png", "jpg", "jpeg"]

def login_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(current_user.is_authenticated)
        if current_user.is_authenticated:
            return func(*args, **kwargs)

        return redirect('/auth/login')
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

def draft_access_required(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(draft_hash: str, *args, **kwargs):
        from app.models import Draft

        draft_id = decode(draft_hash)
        if draft_id is False: return "Draft not found", 404

        draft = Draft.query.get(draft_id)
        print(f"User {current_user.is_authenticated} accessing draft {draft_id}")
        if not isinstance(draft, Draft): return "Draft not found", 404
        if not current_user.has_access_to(draft): return "Access denied", 403

        return func(draft, *args, **kwargs)
    return wrapper


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

@app.route('/proxy-image')
def proxy_image():
    url = request.args.get('url')
    if not url: return "URL parameter is required", 400
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return send_file(
            BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg'),
            as_attachment=False
        )
    except requests.RequestException as e:
        return f"Error fetching image: {str(e)}", 500
