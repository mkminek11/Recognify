
import os.path
import shutil
from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user
from app.models import Draft, DraftImage, DraftLabel, Image, Set, User
from app.app import VALID_IMG_EXTENSIONS, db, UPLOAD_PATH, hid, decode
from app.presentation import extract_images, get_free_filename, get_free_index, temp_remove
import requests

bp = Blueprint("api", __name__, url_prefix = "/api")



@bp.route('/')
def api_index():
    return "API is running"



@bp.route('/presentation', methods=['POST'])
def process_presentation():
    print("Processing presentation...", request.files["presentation"], request.form["draft"])
    presentation = request.files['presentation']
    if not presentation: return jsonify({"error": "No presentation file provided."}), 400

    draft_hash = request.form.get('draft', '')
    draft_id = decode(draft_hash)
    if not draft_id: return jsonify({"error": "No draft ID provided."}), 400

    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    print("Draft found:", draft.id)

    result = extract_images(presentation, draft.id)
    if not result: return jsonify({"error": "Failed to process presentation."}), 500

    print("Processing result:", result)

    tmp_addr, images, labels = result
    temp_remove(tmp_addr)
    return jsonify({"images": images, "labels": labels}), 200



@bp.route('/draft', methods=['DELETE'])
def delete_all_drafts():
    user = current_user
    if not isinstance(user, User) or not user.is_authenticated or not user.permission >= 1:
        return jsonify({"error": "Unauthorized."}), 403
    sets_path = os.path.join(UPLOAD_PATH, "sets")
    shutil.rmtree(sets_path)
    os.makedirs(sets_path, exist_ok=True)

    # Use bulk deletes via the query API to remove rows safely
    DraftImage.query.delete()
    DraftLabel.query.delete()
    Draft.query.delete()
    Image.query.delete()
    Set.query.delete()
    db.session.commit()
    return "", 204



@bp.route('/draft/<string:draft_hash>/', methods=['DELETE'])
def delete_draft(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    shutil.rmtree(os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}"))
    DraftImage.query.filter(DraftImage.draft_id == draft.id).delete()
    DraftLabel.query.filter(DraftLabel.draft_id == draft.id).delete()
    db.session.delete(draft)
    db.session.commit()
    return jsonify({"message": "Draft deleted successfully."}), 200



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



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['GET'])
def get_draft_image(draft_hash: str, image_id: int):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    image = db.session.query(DraftImage).join(Draft).filter(
        DraftImage.id == image_id,
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



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['DELETE'])
def delete_draft_image(draft_hash: str, image_id: int):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400

    image = db.session.query(DraftImage).join(Draft).filter(
        DraftImage.id == image_id,
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

    # image_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}", image.filename)
    # if os.path.exists(image_path):
    #     os.remove(image_path)

    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Image deleted successfully."}), 200



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
def add_image(draft_hash: str):
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



@bp.route('/draft/<string:draft_hash>/gallery/url', methods=['POST'])
def add_image_url(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    data: dict[str, str] = request.get_json()
    image_url = data.get('url', '').strip()
    if not image_url: return jsonify({"error": "No image URL provided."}), 400

    try:
        headers = {'User-Agent': 'Recognify/1.0 (Educational Tool; email@example.com)'}
        response = requests.get(image_url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch image from URL: {str(e)}"}), 400

    content_type = response.headers.get('Content-Type', '')
    if 'image' not in content_type:
        return jsonify({"error": "URL does not point to a valid image."}), 400

    extension = content_type.split('/')[-1]
    if not extension in VALID_IMG_EXTENSIONS:
        return jsonify({"error": f"Not a valid image extension: {extension}"}), 400
    
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}")
    index = get_free_index(path, "img", "*")
    filename = get_free_filename(path, extension, "img", index)

    if not filename: return jsonify({"error": "Failed to generate filename."}), 500
    image_path = os.path.join(path, filename)

    with open(image_path, 'wb') as f:
        f.write(response.content)

    i = DraftImage(draft_id, filename, -1, 0)
    db.session.add(i)
    db.session.commit()
    return jsonify({"message": "Image added successfully.", "id": i.id}), 200



@bp.route('/draft/<string:draft_hash>/change/image', methods=['POST'])
def change_image_from_file(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    change_id = request.form.get('change_id', type=int)
    if not change_id: return jsonify({"error": "No change ID provided."}), 400

    image_file = request.files.get('image')
    if not image_file: return jsonify({"error": "No image file provided."}), 400
    draft_image = DraftImage.query.get(change_id)
    if not isinstance(draft_image, DraftImage) or draft_image.draft_id != draft_id:
        return jsonify({"error": "Image not found in draft."}), 404

    extension = os.path.splitext(image_file.filename or "")[1].lower().lstrip('.')
    if not extension in VALID_IMG_EXTENSIONS:
        return jsonify({"error": f"Not a valid image extension: {extension}"}), 400
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}")
    index = get_free_index(path, "img", "*")
    filename = get_free_filename(path, extension, "img", index)

    if not filename: return jsonify({"error": "Failed to generate filename."}), 500
    image_path = os.path.join(path, filename)
    image_file.save(image_path)
    os.remove(os.path.join(path, draft_image.filename))

    draft_image.filename = filename
    db.session.commit()
    return jsonify({"message": "Image changed successfully."}), 200



@bp.route('/draft/<string:draft_hash>/change/url', methods=['POST'])
def change_image_from_url(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    change_id = request.form.get('change_id', 0, type = int)
    if not change_id: return jsonify({"error": "No change ID provided."}), 400

    url = request.form.get('url', '')
    if not url: return jsonify({"error": "No URL provided."}), 400

    draft_image = DraftImage.query.get(change_id)
    if not isinstance(draft_image, DraftImage) or draft_image.draft_id != draft_id:
        return jsonify({"error": "Image not found in draft."}), 404
    
    print(f"Changing image (id {draft_image.id}) to url '{url}'")
    
    try:
        headers = {'User-Agent': 'Recognify/1.0 (Educational Tool; email@example.com)'}
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch image from URL: {str(e)}"}), 400

    content_type = response.headers.get('Content-Type', '')
    if 'image' not in content_type:
        return jsonify({"error": "URL does not point to a valid image."}), 400

    extension = content_type.split('/')[-1]
    if not extension in VALID_IMG_EXTENSIONS:
        return jsonify({"error": f"Not a valid image extension: {extension}"}), 400
    
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft_id}")
    index = get_free_index(path, "img", "*")
    filename = get_free_filename(path, extension, "img", index)

    if not filename: return jsonify({"error": "Failed to generate filename."}), 500
    image_path = os.path.join(path, filename)

    with open(image_path, 'wb') as f:
        f.write(response.content)

    print("image saved.")

    draft_image.filename = filename
    draft_image.slide = -10000

    db.session.commit()
    return jsonify({"message": "Image changed successfully."}), 200



@bp.route('/draft/<string:draft_hash>/submit', methods=['POST'])
def submit_draft(draft_hash: str):
    draft_id = decode(draft_hash)
    if not isinstance(draft_id, int): return jsonify({"error": "Invalid draft hash."}), 400
    draft = Draft.query.get(draft_id)
    if not isinstance(draft, Draft): return jsonify({"error": "Draft not found."}), 404
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403
    if not draft.images: return jsonify({"error": "Draft has no images."}), 400

    set_id = draft.set_id
    if set_id is None:
        set_ = Set(name = draft.name or "Untitled Set", description = draft.description or "", is_public = True)
        db.session.add(set_)
        db.session.commit()

        for img in draft.images:
            if not img.label: continue
            new_img = Image(filename = img.filename, set_id = set_.id, label = img.label)
            db.session.add(new_img)
            set_.images.append(new_img)

        set_id = set_.id
    
    draft.set_id = set_id
    db.session.commit()

    return jsonify({"message": "Draft submitted successfully.", "set_id": hid.encode(set_id)}), 200



@bp.route('/set', methods=['DELETE'])
def delete_all_sets():
    user = current_user
    if not isinstance(user, User) or not user.is_authenticated or not user.permission >= 1:
        return jsonify({"error": "Unauthorized."}), 403
    db.session.delete(Set)
    db.session.delete(Image)
    db.session.commit()
    return "", 204



@bp.route('/set/<string:set_hash>', methods=['DELETE'])
def delete_set(set_hash: str):
    set_id = decode(set_hash)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    set_ = Set.query.get(set_id)
    if not isinstance(set_, Set): return jsonify({"error": "Set not found."}), 404
    if set_.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    db.session.query(Image).filter(Image.set_id == set_.id).delete()
    db.session.delete(set_)
    db.session.commit()
    return jsonify({"message": "Set deleted successfully."}), 200



@bp.route('/set/<string:set_hash>/image/<int:image_id>', methods=['GET'])
def get_set_image(set_hash: str, image_id: int):
    set_id = decode(set_hash)
    print(set_id, image_id)
    if not isinstance(set_id, int): return jsonify({"error": "Invalid set hash."}), 400
    row = db.session.query(Image, Draft).join(Set, Image.set_id == Set.id).join(Draft, Draft.set_id == Set.id).filter(
        Image.id == image_id,
        Set.id == set_id
    ).first()

    if not row: return jsonify({"error": "Image or draft for set not found."}), 404
    image, draft = row

    if not isinstance(image, Image): return jsonify({"error": "Image not found."}), 404

    return send_file(os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}", image.filename)), 200
