
from flask import jsonify, request
from app.routes.api import bp
from app.inaturalist_api import get_inaturalist_image_links
from urllib.parse import unquote

@bp.route('/inaturalist/links', methods=['GET'])
def inaturalist_links():
    species_param = request.args.get('species', '')
    if not species_param:
        return jsonify({"error": "No species provided."}), 400

    species_list = [unquote(s.strip())for s in species_param.split(',') if s.strip()]
    if not species_list:
        return jsonify({"error": "No valid species provided."}), 400

    links = get_inaturalist_image_links(species_list)
    return jsonify({"links": links})
