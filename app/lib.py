
from flask_login import current_user, login_user, logout_user

import re
import os
from functools import wraps
from typing import Callable

from app.routes.main import bp as main_bp
from app.routes.admin import bp as admin_bp
from app.app import app, db, login


app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix = "/admin")

from app.models import User

@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()

db.init_app(app)
login.init_app(app)

with app.app_context():
    db.create_all()
