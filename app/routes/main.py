
from flask import Blueprint, render_template
from app.models import Set
from app.app import db

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/sets')
def index():
    return render_template('index.html', sets = Set.query.all())

@bp.route('/sets/new', methods=['GET'])
def new_set():
    return render_template('new_set.html')

@bp.route('/sets', methods=['DELETE'])
def delete_all_sets():
    Set.query.delete()
    db.session.commit()
    return "", 204

@bp.route('/sets/<int:set_id>')
def set_view(set_id):
    set_ = Set.query.get(set_id)
    if not set_: return "Set not found", 404
    return render_template('set.html', set = set_)
