
from flask import Blueprint, render_template
from app.models import Set

bp = Blueprint("main", __name__)

@bp.route('/')
def index():
    return render_template('index.html', sets = Set.query.all())
