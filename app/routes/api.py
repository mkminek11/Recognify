
from flask import Blueprint, jsonify, request
from app.models import Set
from app.app import db
from app import presentation

bp = Blueprint("api", __name__, url_prefix = "/api")

@bp.route('/')
def api_index():
    return "API is running"

@bp.route('/presentation', methods=['POST'])
def process_presentation():
    PRESENTATION = request.files['presentation']
    if not PRESENTATION: return jsonify({"error": "No presentation file provided."}), 400
    
    presentation.extract_images(PRESENTATION)

    return jsonify({"message": "Presentation processed successfully."})
