
from flask import Blueprint, redirect, render_template
from flask_login import current_user
from app.models import Draft, Set
from app.app import db, login_required
from app.presentation import create_draft

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/sets')
@login_required
def index():
    return render_template('index.html', sets = Set.query.all(), drafts = Draft.query.where(Draft.owner_id == current_user.id).all())

@bp.route('/sets/new', methods=['GET'])
@login_required
def new_set():
    draft = create_draft()
    return redirect(f'/draft/{draft}')

@bp.route('/sets', methods=['DELETE'])
@login_required
def delete_all_sets():
    Set.query.delete()
    db.session.commit()
    return "", 204

@bp.route('/sets/<int:set_id>')
@login_required
def set_view(set_id):
    set_ = Set.query.get(set_id)
    if not set_: return "Set not found", 404
    return render_template('set.html', set = set_)

@bp.route('/draft/<int:draft_id>')
@login_required
def draft_view(draft_id: int):
    print("Draft ID:", draft_id)
    draft = Draft.query.get(draft_id)
    if not draft: return "Draft not found", 404
    return render_template('draft.html', draft = draft)
