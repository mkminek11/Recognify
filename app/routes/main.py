
from flask import Blueprint, redirect, render_template
from app.models import Draft, Set
from app.app import db
from app.presentation import create_draft

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/sets')
def index():
    return render_template('index.html', sets = Set.query.all())

@bp.route('/sets/new', methods=['GET'])
def new_set():
    draft = create_draft()
    return redirect(f'/drafts/{draft}')

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

@bp.route('/drafts/<int:draft_id>')
def drafts(draft_id: int):
    print("Draft ID:", draft_id)
    draft = Draft.query.get(draft_id)
    if not draft: return "Draft not found", 404
    return render_template('draft.html', draft = draft)
