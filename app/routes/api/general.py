
import os.path
from flask_login import current_user
from flask import jsonify, request, send_file
from app.models import Draft, Image, Set, SkipImage, User
from app.app import db, UPLOAD_PATH, decode, decode_image, log_info
from app.routes.api import bp


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
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return jsonify({"error": "Set not found."}), 404
    if set_.owner != current_user: return jsonify({"error": "Unauthorized."}), 403
    data: dict[str, int] = request.get_json()
    image_id = data.get('image_id', 0)
    image = Image.query.get(image_id)
    if not isinstance(image, Image) or image.set_id != set_.id:
        return jsonify({"error": "Image not found in set."}), 404
    
    si = SkipImage(current_user.id, image_id)
    db.session.add(si)
    db.session.commit()
    return jsonify({"message": "Image marked as skipped."}), 200