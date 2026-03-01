
from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user
from urllib.parse import unquote
import os.path

from app.models import Draft, DraftAccess, Image, Set, SkipImage, User, UserSettings
from app.app import db, UPLOAD_PATH, decode, decode_image, encode, get_data, log_info, login_required
from app.lib.inaturalist_api import get_inaturalist_image_links


bp = Blueprint('api_general', __name__, url_prefix='/api')


@bp.route('/')
def api_index():
    return "API is running"



@bp.route('/sets', methods=['DELETE'])
def delete_all_sets():
    user = current_user
    if not isinstance(user, User) or not user.is_authenticated or not user.permission >= 1:
        return jsonify({"error": "Unauthorized."}), 403
    db.session.query(Image).delete()
    db.session.query(Set).delete()
    db.session.commit()

    log_info(f"All sets deleted by admin user {user.username} ({user.id}).")

    return "", 204



@bp.route('/sets/<string:set_hash>', methods=['DELETE'])
def delete_set(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return jsonify({"error": "Set not found."}), 404
    if set_.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    db.session.query(Image).filter(Image.set_id == set_.id).delete()
    db.session.delete(set_)
    db.session.commit()

    log_info(f"Set {set_.name} ({set_.id}) deleted by user {current_user.username} ({current_user.id}).")

    return jsonify({"message": "Set deleted successfully."}), 200



@bp.route('/sets/<string:set_hash>/image/<string:image_hash>', methods=['GET'])
def get_set_image(set_hash: str, image_hash: str):
    set_id = decode(set_hash)
    image_id = decode_image(image_hash, set_id)
    if image_id is False: return jsonify({"error": "Invalid set or image hash."}), 400

    row = db.session.query(Image, Draft).join(Set, Image.set_id == Set.id).join(Draft, Draft.set_id == Set.id).filter(
        Image.id == image_id,
        Set.id == set_id
    ).first()

    if not row: return jsonify({"error": "Image or draft for set not found."}), 404
    image, draft = row

    if not isinstance(image, Image): return jsonify({"error": "Image not found."}), 404

    return send_file(os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}", image.filename)), 200



@bp.route('/sets/<string:set_hash>/skip', methods=['POST'])
def skip_set_image(set_hash: str):
    if not current_user.is_authenticated: return jsonify({"error": "Unauthorized."}), 403
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return jsonify({"error": "Set not found."}), 404
    data: dict[str, int] = request.get_json()
    image_id = decode_image(str(data.get('image_id', '')), set_id)
    image = Image.query.get(image_id)
    if not isinstance(image, Image) or image.set_id != set_.id:
        return jsonify({"error": "Image not found in set."}), 404
    
    si = SkipImage(current_user.id, image_id)
    db.session.add(si)
    db.session.commit()
    return jsonify({"message": "Image marked as skipped."}), 200



@bp.route('/sets/<string:set_hash>/skip', methods=['DELETE'])
def remove_skip_set_image(set_hash: str):
    if not current_user.is_authenticated: return jsonify({"error": "Unauthorized."}), 403
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return jsonify({"error": "Set not found."}), 404
    data: dict[str, int] = request.get_json()
    image_id = decode_image(str(data.get('image_id', '')), set_id)
    image = Image.query.get(image_id)
    if not isinstance(image, Image) or image.set_id != set_.id:
        return jsonify({"error": "Image not found in set."}), 404
    
    si = SkipImage(current_user.id, image_id)
    db.session.add(si)
    db.session.commit()
    return jsonify({"message": "Image marked as skipped."}), 200



@bp.route('/inaturalist/links', methods=['GET'])
def inaturalist_links():
    try:
        species_param = request.args.get('species', '')
        if not species_param:
            return jsonify({"error": "No species provided."}), 400

        species_list = [unquote(s.strip()) for s in species_param.split(',') if s.strip()]
        if not species_list:
            return jsonify({"error": "No valid species provided."}), 400

        # Limit to prevent timeout issues
        MAX_SPECIES = 50
        if len(species_list) > MAX_SPECIES:
            return jsonify({"error": f"Too many species requested. Maximum is {MAX_SPECIES}, you requested {len(species_list)}. Please split into smaller batches."}), 400

        log_info(f"Fetching iNaturalist links for {len(species_list)} species...")
        links = get_inaturalist_image_links(species_list)
        log_info(f"Successfully fetched links for {len(links)} species")
        return jsonify({"links": links})
    except Exception as e:
        log_info(f"Error in inaturalist_links: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch iNaturalist links: {str(e)}"}), 500



@bp.route('/search', methods=['GET'])
def api_search():
    query = request.args.get('q', '')

    SET_LIMIT = 10
    USER_LIMIT = 5

    if current_user.is_authenticated:
        sets: list[Set] = Set.query.join(Draft, Set.id == Draft.set_id)\
            .outerjoin(DraftAccess, Draft.id == DraftAccess.draft_id)\
            .where(
                Set.name.ilike(f'%{query}%'),
                (Set.is_public == True) | 
                (Set.owner_id == current_user.id) | 
                (Draft.owner_id == current_user.id) |
                (DraftAccess.user_id == current_user.id)
            ).limit(SET_LIMIT).distinct().all()
    else:
        sets: list[Set] = Set.query.where(
            Set.name.ilike(f'%{query}%'),
            Set.is_public == True
        ).limit(SET_LIMIT).all()

    users: list[User] = User.query.where(User.username.ilike(f'%{query}%')).limit(USER_LIMIT).all()

    set_data = [
        {
            "id": set_.hid(),
            "name": set_.name,
            "url": f"/sets/{set_.hid()}"
        } for set_ in sets
    ]

    user_data = [
        {
            "id": user.hid(),
            "name": user.username,
            "url": f"/profile/{user.hid()}"
        } for user in users
    ]

    print(set_data, user_data)

    return jsonify({"sets": set_data, "users": user_data}), 200


@login_required
@bp.route('/user/settings', methods=['GET'])
def get_user_settings():
    if not isinstance(current_user, User): return jsonify({"error": "Unauthorized."}), 403
    settings = current_user.settings()

    return jsonify({
        "theme": settings.theme,
        "keyboard_controls": settings.keyboard_controls,
        "mouse_controls": settings.mouse_controls
    }), 200



@login_required
@bp.route('/user/settings', methods=['POST'])
def update_user_settings():
    if not isinstance(current_user, User): return jsonify({"error": "Unauthorized."}), 403
    data: dict[str, str|bool] = request.get_json()
    settings = current_user.settings()

    for key, value in data.items():
        if key in UserSettings.all():
            target_type = type(getattr(settings, key))
            if not isinstance(value, target_type):
                try:
                    value = target_type(value)
                except ValueError:
                    continue
            setattr(settings, key, value)

    db.session.commit()

    return jsonify({"message": "Settings updated successfully."}), 200
