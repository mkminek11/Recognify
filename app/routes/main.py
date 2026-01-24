
from flask import Blueprint, jsonify, redirect, render_template, request
from flask_login import current_user
from app.models import Draft, Image, Set, SkipImage, User
from app.app import db, draft_access_required, encode, get_data, login_required, decode, encode, log_info, set_access_required
from app.lib.presentation import create_draft

bp = Blueprint("main", __name__)

@bp.route('/')
@bp.route('/sets')
def index():
    sets = Set.all_for(current_user)
    drafts = []

    if current_user.is_authenticated:
        drafts = current_user.get_drafts()
    
    return render_template('index.html', sets = sets, drafts = drafts, popular_sets = sets[:5])

@bp.route('/search')
def search():
    query = request.args.get('q', '')

    results = []
    results.extend(Set.query.where(Set.name.ilike(f'%{query}%')).all())
    results.extend(filter(lambda x: x not in results, Set.query.where(Set.description.ilike(f'%{query}%')).all()))

    return render_template('search.html', search_query = query, search_results = results)

@bp.route('/sets/new', methods=['GET'])
@login_required
def new_set():
    draft_id = create_draft()
    log_info(f"User {current_user.username} created a new draft {draft_id}")
    return redirect(f'/draft/{encode(draft_id)}')

@bp.route('/sets/<string:set_hash>')
@set_access_required
def view_set(set_: Set):
    return render_template('set_view.html', set = set_)

@bp.route('/sets/<string:set_hash>/cards')
def set_cards(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return "Invalid set hash", 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return "Set not found", 404

    return render_template('set_cards.html', set = set_, anonymous = current_user.is_anonymous)

@bp.route('/draft/<string:draft_hash>')
@draft_access_required
def draft_view(draft: Draft):
    if not current_user.is_authenticated or not current_user.has_access_to(draft): return "Access denied", 403
    
    return render_template('draft.html', draft = draft)

@bp.route('/settings')
@login_required
def settings():
    return render_template('not_implemented.html')

@bp.route('/profile/<string:user_hash>')
def profile(user_hash: str):
    user_id = decode(user_hash)
    if not isinstance(user_id, int): return "User not found", 400
    user = db.session.execute(User.query.where(User.id == user_id)).scalar_one_or_none()
    if not isinstance(user, User): return "User not found", 404

    return render_template('not_implemented.html', data = {"user": user})

@bp.route('/profile')
@login_required
def my_profile():
    return redirect(f'/profile/{current_user.hid()}')

@bp.route('/profile/sets')
@login_required
def my_sets():
    user = db.session.execute(User.query.where(User.id == current_user.id)).scalar_one_or_none()
    return render_template('not_implemented.html', data = {"user": user})
