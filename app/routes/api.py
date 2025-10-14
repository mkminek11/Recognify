
import os.path
from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user
from app.models import Draft, DraftImage, DraftLabel, Image, Set
from app.app import db, UPLOAD_PATH, hid, decode
from app.presentation import extract_images, get_free_filename, get_free_index, temp_remove

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



@bp.route('/draft/<string:draft_hash>/rename', methods=['POST'])
def rename_draft(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    data: dict[str, str] = request.get_json()
    new_title = data.get('title', '').strip()
    if not new_title: return jsonify({"error": "Title cannot be empty."}), 400

    draft.name = new_title
    db.session.commit()
    return jsonify({"message": "Draft renamed successfully.", "new_title": draft.name}), 200



@bp.route('/draft/<string:draft_hash>/description', methods=['POST'])
def update_draft_description(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    data: dict[str, str] = request.get_json()
    new_description = data.get('description', '').strip()

    draft.description = new_description
    db.session.commit()
    return jsonify({"message": "Draft description updated successfully.", "new_description": draft.description}), 200



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['POST'])
def update_image_label(draft_hash: str, image_id: int):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    image = DraftImage.query.get(image_id)
    if not isinstance(image, DraftImage) or image.draft_id != draft_id:
        return jsonify({"error": "Image not found in draft."}), 404

    data: dict[str, str] = request.get_json()
    new_label = data.get('label', '').strip()

    image.label = new_label
    db.session.commit()
    return jsonify({"message": "Image label updated successfully.", "new_label": image.label}), 200



@bp.route('/draft/<string:draft_hash>/gallery', methods=['GET'])
def fetch_gallery(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    images = [{"id": img.id, "filename": img.filename, "label": img.label, "slide": img.slide} for img in draft.images]
    labels = [{"text": lbl.label, "slide": lbl.slide} for lbl in draft.labels]
    return jsonify({"images": images, "labels": labels}), 200



@bp.route('/draft/<string:draft_hash>/gallery', methods=['POST'])
def update_gallery(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    images = request.files.getlist('images')
    if not images: return jsonify({"error": "No image files provided."}), 400

    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}")
    index = get_free_index(path, "img", "*")
    for image in images:
        extension = os.path.splitext(image.filename or "")[1].lower().lstrip('.')
        os.makedirs(path, exist_ok=True)
        filename = get_free_filename(path, extension, "img", index)

        if not filename: return jsonify({"error": "Failed to generate filename."}), 500
        image_path = os.path.join(path, filename)
        image.save(image_path)

        i = DraftImage(draft_id, filename, 0, 0)
        db.session.add(i)
    db.session.commit()
    return jsonify({"message": "Gallery updated successfully."}), 200



@bp.route('/draft/<string:draft_hash>/image/<string:filename>', methods=['GET'])
def get_draft_image(draft_hash: str, filename: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
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



@bp.route('/draft/<string:draft_hash>/submit', methods=['POST'])
def submit_draft(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403
    if draft.set_id is not None: return jsonify({"error": "Draft has already been submitted."}), 400
    if not draft.images: return jsonify({"error": "Draft has no images."}), 400

    set_ = Set(name = draft.name or "Untitled Set", description = draft.description or "", is_public = True)
    db.session.add(set_)
    db.session.commit()

    for img in draft.images:
        new_img = Image(filename = img.filename, set_id = set_.id, label = img.label)
        db.session.add(new_img)
        set_.images.append(new_img)
    
    draft.set_id = set_.id
    db.session.commit()

    return jsonify({"message": "Draft submitted successfully.", "set_id": hid.encode(set_.id)}), 200
