
import os.path
from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user
from app.models import Draft, DraftImage, Image, Set
from app.app import db, UPLOAD_PATH
from app.presentation import extract_images, temp_remove

bp = Blueprint("api", __name__, url_prefix = "/api")

@bp.route('/')
def api_index():
    return "API is running"

@bp.route('/presentation', methods=['POST'])
def process_presentation():
    print("Processing presentation...", request.files, request.form)
    presentation = request.files['presentation']
    if not presentation: return jsonify({"error": "No presentation file provided."}), 400

    draft_id = request.form.get('draft', '')
    if not draft_id: return jsonify({"error": "No draft ID provided."}), 400

    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    result = extract_images(presentation, draft.id)
    if not result: return jsonify({"error": "Failed to process presentation."}), 500

    tmp_addr, images, labels = result
    temp_remove(tmp_addr)
    return jsonify({"images": images, "labels": labels}), 200

@bp.route('/draft/<int:draft_id>/rename', methods=['POST'])
def rename_draft(draft_id):
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    data: dict[str, str] = request.get_json()
    new_title = data.get('title', '').strip()
    if not new_title: return jsonify({"error": "Title cannot be empty."}), 400

    draft.name = new_title
    db.session.commit()
    return jsonify({"message": "Draft renamed successfully.", "new_title": draft.name}), 200

@bp.route('/draft/<int:draft_id>/description', methods=['POST'])
def update_draft_description(draft_id):
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    data: dict[str, str] = request.get_json()
    new_description = data.get('description', '').strip()

    draft.description = new_description
    db.session.commit()
    return jsonify({"message": "Draft description updated successfully.", "new_description": draft.description}), 200

@bp.route('/draft/<int:draft_id>/gallery', methods=['GET'])
def fetch_gallery(draft_id: int):
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    images = [{"filename": img.filename, "label": img.label, "slide": img.slide} for img in draft.images]
    labels = [{"text": lbl.label, "slide": lbl.slide} for lbl in draft.labels]
    return jsonify({"images": images, "labels": labels}), 200

@bp.route('/draft/<int:draft_id>/image/<string:filename>', methods=['GET'])
def get_draft_image(draft_id: int, filename: str):
    image = db.session.query(DraftImage).join(Draft).filter(
        DraftImage.filename == filename,
        DraftImage.draft_id == draft_id,
        Draft.owner == current_user
    ).first()
    
    if not image:
        draft = Draft.query.get(draft_id)
        if not draft:
            return jsonify({"error": "Draft not found."}), 404
        elif draft.owner != current_user:
            return jsonify({"error": "Unauthorized."}), 403
        else:
            return jsonify({"error": "Image not found in draft."}), 404

    image_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}", image.filename)
    if not os.path.exists(image_path): return jsonify({"error": "Image file not found."}), 404
    
    return send_file(image_path)
