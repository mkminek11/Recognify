
from flask_login import current_user, login_user, logout_user

from functools import wraps
from typing import Callable
import logging
import sys

import app.routes # Assign blueprints
from app.app import app, db, login
from app.models import User

# Redirect Werkzeug reloader messages to stdout only
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = []
werkzeug_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(message)s'))
werkzeug_logger.addHandler(console_handler)
werkzeug_logger.propagate = False

@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id = user_id).first()

db.init_app(app)
login.init_app(app)

with app.app_context():
    db.create_all()
