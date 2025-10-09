
import os.path
from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.models import Draft, Set
from app.app import UPLOAD_PATH, db
from app.presentation import extract_images

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

    extract_images(presentation, draft.id)

    return jsonify({"message": "Presentation processed successfully."})
