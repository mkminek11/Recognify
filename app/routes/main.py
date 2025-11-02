
from flask import Blueprint, jsonify, redirect, render_template
from flask_login import current_user
from app.models import Draft, Image, Set, SkipImage
from app.app import db, login_required, hid, decode
from app.presentation import create_draft

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/set')
def index():
    sets = [{ "id": hid.encode(set.id), "name": set.name } for set in Set.query.all()]

    drafts = []
    if current_user.is_authenticated:
        drafts = [
            { "id": hid.encode(draft.id), "name": draft.name }
            for draft in Draft.query.where(Draft.owner_id == current_user.id).all()]
    
    return render_template('index.html', sets = sets, drafts = drafts)

@bp.route('/set/new', methods=['GET'])
@login_required
def new_set():
    draft_id = create_draft()
    return redirect(f'/draft/{hid.encode(draft_id)}')

@bp.route('/set/<string:set_hash>')
def view_set(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return "Invalid set hash", 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return "Set not found", 404

    draft = Draft.query.filter(Draft.set_id == set_.id).first()
    if not isinstance(draft, Draft): return "Associated draft not found", 404
    
    data = {
        "id": set_hash,
        "name": set_.name,
        "draft_id": hid.encode(draft.id),
        "description": set_.description,
        "created_at": set_.created_at.isoformat(),
        "images": [
            { "id": i.id, "label": i.label } for i in set_.images
        ]
    }
    
    return render_template('set_view.html', set = data)

@bp.route('/set/<string:set_hash>/play')
def play_set(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return "Invalid set hash", 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return "Set not found", 404

    user_id = current_user.id if current_user.is_authenticated else -1
    img_query = Image.query\
                .outerjoin(SkipImage, (Image.id == SkipImage.image_id) & (SkipImage.user_id == user_id))\
                .where(Image.set_id == set_.id, SkipImage.id == None).all()

    images = [{ "id": i.id, "filename": i.filename, "label": i.label } for i in img_query]

    data = {
        "id": set_.hash(),
        "name": set_.name,
        "description": set_.description,
        "created_at": set_.created_at.isoformat(),
        "hash": set_.hash(),
        "images": images
    }

    return render_template('play_set.html', set = data, anonymous = int(current_user.is_anonymous))

@bp.route('/draft/<string:draft_hash>')
@login_required
def draft_view(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return "Invalid draft hash", 400
    draft = Draft.query.get(draft_id)

    if not isinstance(draft, Draft) or current_user.is_anonymous or draft.owner_id != current_user.id:
        return "Draft not found", 404
    
    return render_template('draft.html', draft = draft)
