
import datetime
import logging
import sys

from app import routes # Assign blueprints
from app.app import app, db, get_data, login
from app.models import Draft, Set, User

# Redirect Werkzeug reloader messages to stdout only
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.handlers = []
werkzeug_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(message)s'))
werkzeug_logger.addHandler(console_handler)
werkzeug_logger.propagate = False

@login.user_loader
def load_user(user_id: int) -> User | None:
    return User.query.filter_by(id = user_id).first()

@app.context_processor
def inject_user():
    return {"User": User, "Draft": Draft, "Set": Set, "datetime": datetime, "get_data": get_data}

db.init_app(app)
login.init_app(app)

with app.app_context():
    db.create_all()
