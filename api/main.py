from flask import Flask, request, jsonify
import hashids
from db import *

hid = hashids.Hashids(min_length = 8, salt = "ref4a9wzs7")

@app.route('/api')
def index():
    return jsonify("Pong!")

@app.route('/api/sets', methods=['GET'])
def get_sets():
    return jsonify([{ "id": hid.encode(set.id), "name": set.name } for set in Set.all()])

@app.route('/api/sets/<string:set_id>', methods=['GET'])
def get_set(set_id: str):
    decoded = hid.decode(set_id)
    if not decoded: return jsonify({ "error": "Set not found" }), 404

    set = db.session.get(Set, decoded[0])
    if not isinstance(set, Set): return jsonify({ "error": "Set not found" }), 404

    return jsonify({
        "id": hid.encode(set.id),
        "name": set.name,
        "description": set.description,
        "is_public": set.is_public,
        "created_at": set.created_at.isoformat(),
        "owner": {
            "id": hid.encode(set.owner.id),
            "username": set.owner.username
        },
        "images": [
            {
                "id": hid.encode(image.id),
                "filename": image.filename,
                "original_filename": image.original_filename,
                "label": {
                    "id": hid.encode(image.label.id),
                    "name": image.label.name
                } if image.label else None
            } for image in set.images
        ],
        "labels": [
            {
                "id": hid.encode(label.id),
                "name": label.name,
                "image_count": len(label.images)
            } for label in set.labels
        ]
    }), 200

if __name__ == "__main__":
    app.run(debug = True)
