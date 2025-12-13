
import shutil
import os.path
import requests
from flask_login import current_user
from flask import jsonify, request, send_file
from app.models import Draft, DraftAccess, DraftImage, DraftLabel, Image, Set, SkipImage, User
from app.app import VALID_IMG_EXTENSIONS, db, UPLOAD_PATH, draft_access_required, hid, decode, permission_required
from app.presentation import extract_images, get_free_filename, get_free_index, temp_remove
from app.routes.api import bp



@bp.route('/draft/<string:draft_hash>/presentation', methods=['POST'])
@draft_access_required
def process_presentation(draft: Draft):
    print("Processing presentation...", request.files["presentation"], request.form["draft"])
    presentation = request.files['presentation']
    if not presentation: return jsonify({"error": "No presentation file provided."}), 400

    result = extract_images(presentation, draft.id)
    if not result: return jsonify({"error": "Failed to process presentation."}), 500

    print("Processing result:", result)

    tmp_addr, images, labels = result
    temp_remove(tmp_addr)
    return jsonify({"images": images, "labels": labels}), 200



@bp.route('/draft', methods=['DELETE'])
@permission_required(10)
def delete_all_drafts():
    sets_path = os.path.join(UPLOAD_PATH, "sets")
    shutil.rmtree(sets_path)
    os.makedirs(sets_path, exist_ok=True)

    db.session.query(DraftImage).delete()
    db.session.query(DraftLabel).delete()
    db.session.query(DraftAccess).delete()
    db.session.query(Draft).delete()
    db.session.query(Image).delete()
    db.session.query(Set).delete()
    db.session.commit()
    return "", 204



@bp.route('/draft/<string:draft_hash>/', methods=['DELETE'])
@draft_access_required
def delete_draft(draft: Draft):
    draft_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")
    if os.path.exists(draft_path):
        shutil.rmtree(draft_path)
    DraftImage.query.filter(DraftImage.draft_id == draft.id).delete()
    DraftLabel.query.filter(DraftLabel.draft_id == draft.id).delete()
    DraftAccess.query.filter(DraftAccess.draft_id == draft.id).delete()
    image_ids = [i.id for i in Image.query.filter(Image.set_id == draft.set_id).all()]
    SkipImage.query.filter(SkipImage.image_id.in_(image_ids)).delete(synchronize_session=False)
    Image.query.filter(Image.set_id == draft.set_id).delete()
    Set.query.filter(Set.id == draft.set_id).delete()
    db.session.delete(draft)
    db.session.commit()
    return jsonify({"message": "Draft deleted successfully."}), 200



@bp.route('/draft/<string:draft_hash>/rename', methods=['POST'])
@draft_access_required
def rename_draft(draft: Draft):
    data: dict[str, str] = request.get_json()
    new_title = data.get('title', '').strip()
    if not new_title: return jsonify({"error": "Title cannot be empty."}), 400

    draft.name = new_title
    db.session.commit()
    return jsonify({"message": "Draft renamed successfully.", "new_title": draft.name}), 200



@bp.route('/draft/<string:draft_hash>/description', methods=['POST'])
@draft_access_required
def update_draft_description(draft: Draft):
    data: dict[str, str] = request.get_json()
    new_description = data.get('description', '').strip()

    draft.description = new_description
    db.session.commit()
    return jsonify({"message": "Draft description updated successfully.", "new_description": draft.description}), 200



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['POST'])
@draft_access_required
def update_image_label(draft: Draft, image_id: int):
    image = DraftImage.query.get(image_id)
    if not isinstance(image, DraftImage) or image.draft_id != draft.id:
        return jsonify({"error": "Image not found in draft."}), 404

    data: dict[str, str] = request.get_json()
    new_label = data.get('label', '').strip()

    image.label = new_label
    db.session.commit()
    return jsonify({"message": "Image label updated successfully.", "new_label": image.label}), 200



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['GET'])
@draft_access_required
def get_draft_image(draft: Draft, image_id: int):
    image = db.session.query(DraftImage).join(Draft).filter(
        DraftImage.id == image_id,
        DraftImage.draft_id == draft.id,
        Draft.owner == current_user
    ).first()
    
    if not image:
        return jsonify({"error": "Image not found in draft."}), 404

    image_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}", image.filename)
    if not os.path.exists(image_path): return jsonify({"error": "Image file not found."}), 404
    
    return send_file(image_path)



@bp.route('/draft/<string:draft_hash>/image/<int:image_id>', methods=['DELETE'])
@draft_access_required
def delete_draft_image(draft: Draft, image_id: int):
    image = db.session.query(DraftImage).join(Draft).filter(
        DraftImage.id == image_id,
        DraftImage.draft_id == draft.id
    ).first()

    if not image:
        return jsonify({"error": "Image not found in draft."}), 404

    # image_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}", image.filename)
    # if os.path.exists(image_path):
    #     os.remove(image_path)

    db.session.delete(image)
    db.session.commit()
    return jsonify({"message": "Image deleted successfully."}), 200



@bp.route('/draft/<string:draft_hash>/gallery', methods=['GET'])
@draft_access_required
def fetch_gallery(draft: Draft):
    """ Fetches all images and labels for a draft """
    images = [{"id": img.id, "filename": img.filename, "label": img.label, "slide": img.slide} for img in draft.images]
    labels = [{"text": lbl.label, "slide": lbl.slide} for lbl in draft.labels]
    return jsonify({"images": images, "labels": labels}), 200



@bp.route('/draft/<string:draft_hash>/gallery', methods=['POST'])
@draft_access_required
def add_image(draft: Draft):
    """ Add image to draft from files """
    images = request.files.getlist('images')
    if not images: return jsonify({"error": "No image files provided."}), 400

    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")
    index = get_free_index(path, "img", "*")
    added_images = []
    for image in images:
        extension = os.path.splitext(image.filename or "")[1].lower().lstrip('.')
        os.makedirs(path, exist_ok=True)
        filename = get_free_filename(path, extension, "img", index)

        if not filename: return jsonify({"error": "Failed to generate filename."}), 500
        image_path = os.path.join(path, filename)
        image.save(image_path)

        i = DraftImage(draft.id, filename, 0, 0)
        db.session.add(i)
        db.session.flush()
        added_images.append({"id": i.id, "filename": i.filename, "label": i.label, "slide": i.slide})
    db.session.commit()
    return jsonify({"images": added_images}), 200



@bp.route('/draft/<string:draft_hash>/gallery/url', methods=['POST'])
@draft_access_required
def add_image_url(draft: Draft):
    """ Add image to draft gallery from URL """
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
    
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")
    index = get_free_index(path, "img", "*")
    filename = get_free_filename(path, extension, "img", index)

    if not filename: return jsonify({"error": "Failed to generate filename."}), 500
    image_path = os.path.join(path, filename)

    with open(image_path, 'wb') as f:
        f.write(response.content)

    i = DraftImage(draft.id, filename, -1, 0)
    db.session.add(i)
    db.session.commit()
    return jsonify({"message": "Image added successfully.", "id": i.id}), 200



@bp.route('/draft/<string:draft_hash>/change/image', methods=['POST'])
@draft_access_required
def change_image_from_file(draft: Draft):
    change_id = request.form.get('change_id', type=int)
    if not change_id: return jsonify({"error": "No change ID provided."}), 400

    image_file = request.files.get('image')
    if not image_file: return jsonify({"error": "No image file provided."}), 400
    draft_image = DraftImage.query.get(change_id)
    if not isinstance(draft_image, DraftImage) or draft_image.draft_id != draft.id:
        return jsonify({"error": "Image not found in draft."}), 404

    extension = os.path.splitext(image_file.filename or "")[1].lower().lstrip('.')
    if not extension in VALID_IMG_EXTENSIONS:
        return jsonify({"error": f"Not a valid image extension: {extension}"}), 400
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")
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
@draft_access_required
def change_image_from_url(draft: Draft):
    if draft.owner != current_user: return jsonify({"error": "Unauthorized."}), 403

    change_id = request.form.get('change_id', 0, type = int)
    if not change_id: return jsonify({"error": "No change ID provided."}), 400

    url = request.form.get('url', '')
    if not url: return jsonify({"error": "No URL provided."}), 400

    draft_image = DraftImage.query.get(change_id)
    if not isinstance(draft_image, DraftImage) or draft_image.draft_id != draft.id:
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
    
    path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")
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
@draft_access_required
def publish_draft(draft: Draft):
    if not current_user.is_authenticated or not current_user.has_access_to(draft): return jsonify({"error": "Unauthorized."}), 403
    if not draft.images: return jsonify({"error": "Draft has no images."}), 400

    set_id = draft.set_id
    if set_id is None:
        # Create new set
        set_ = Set(name = draft.name or "Untitled Set", description = draft.description or "", is_public = True)
        db.session.add(set_)
        db.session.commit()

        for img in draft.images:
            if not img.label: continue
            new_img = Image(filename = img.filename, set_id = set_.id, label = img.label)
            db.session.add(new_img)
            set_.images.append(new_img)

        draft.set_id = set_.id
        db.session.commit()
    else:
        # Update existing set
        set_ = Set.query.get(set_id)
        if not isinstance(set_, Set):
            return jsonify({"error": "Associated set not found."}), 404
        set_.name = draft.name or set_.name
        set_.description = draft.description or set_.description

        set_images = {img.filename: False for img in set_.images}
        for draft_img in draft.images:
            if draft_img.filename in set_images:
                # Existing image, update label
                img = Image.query.filter_by(filename=draft_img.filename).first()
                if not isinstance(img, Image): continue
                img.label = draft_img.label
                set_images[draft_img.filename] = True
            else:
                # New image, add to set
                new_img = Image(filename = draft_img.filename, set_id = set_.id, label = draft_img.label, draft_image_id = draft_img.id)
                db.session.add(new_img)
                set_.images.append(new_img)
        
        for img_id, found in set_images.items():
            if found: continue

            img = Image.query.get(img_id)
            if not isinstance(img, Image): continue
            SkipImage.query.filter(SkipImage.image_id == img.id).delete()
            db.session.delete(img)

        db.session.commit()

    return jsonify({"message": "Draft published successfully.", "set_id": hid.encode(set_id)}), 200



@bp.route('/draft/<string:draft_hash>/access', methods=['POST'])
@draft_access_required
def add_draft_access(draft: Draft):
    data = request.get_json()
    user = data.get("user", "").strip()
    if not user: return jsonify({"error": "No user provided."}), 400

    user_obj = User.query.filter((User.email == user) | (User.username == user)).first()
    if not isinstance(user_obj, User): return jsonify({"error": "User not found."}), 404

    draft_access = DraftAccess(draft_id = draft.id, user_id = user_obj.id)
    db.session.add(draft_access)
    db.session.commit()

    return jsonify({"message": "Access granted successfully.", 
                    "user": { "id": user_obj.id, "name": user_obj.username, "email": user_obj.email }}), 200



@bp.route('/draft/<string:draft_hash>/access', methods=['DELETE'])
@draft_access_required
def remove_draft_access(draft: Draft):
    data = request.get_json()
    user = data.get("user", "").strip()
    # TODO

    print(request.get_json())
    return ""
