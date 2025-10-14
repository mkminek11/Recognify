
from flask import Blueprint, redirect, render_template
from flask_login import current_user
from app.models import Draft, Set
from app.app import db, login_required, hid, decode
from app.presentation import create_draft

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/sets')
@login_required
def index():
    drafts = [{ "id": hid.encode(draft.id), "name": draft.name } for draft in Draft.query.where(Draft.owner_id == current_user.id).all()]
    sets = [{ "id": hid.encode(set.id), "name": set.name } for set in Set.query.all()]
    return render_template('index.html', sets = sets, drafts = drafts)

@bp.route('/sets/new', methods=['GET'])
@login_required
def new_set():
    draft_id = create_draft()
    return redirect(f'/draft/{hid.encode(draft_id)}')

@bp.route('/sets', methods=['DELETE'])
@login_required
def delete_all_sets():
    Set.query.delete()
    db.session.commit()
    return "", 204

@bp.route('/sets/<string:set_hash>')
@login_required
def set_view(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return "Invalid set hash", 400
    set_ = Set.query.get(set_id)
    if not set_: return "Set not found", 404
    return render_template('set.html', set = set_)

@bp.route('/draft/<string:draft_hash>')
@login_required
def draft_view(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return "Invalid draft hash", 400
    draft = Draft.query.get(draft_id)
    if not draft: return "Draft not found", 404
    return render_template('draft.html', draft = draft)
