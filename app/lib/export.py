
from typing import Literal
from flask_login import current_user
from werkzeug.datastructures import FileStorage

from app.app import UPLOAD_PATH, EXPORT_PATH, db
from app.lib.presentation import get_free_filename
from app.models import Draft, DraftImage

import os
import zipfile
import json

def export_draft(draft: Draft) -> str | Literal[False]:
    export_data = {
        "name": draft.name,
        "images": [{ "filename": img.filename, "label": img.label } for img in draft.images]
    }

    os.makedirs(EXPORT_PATH, exist_ok=True)
    filename = get_free_filename(EXPORT_PATH, "zip", "export")

    with zipfile.ZipFile(os.path.join(EXPORT_PATH, filename), 'w') as zip:
        zip.writestr('export.json', json.dumps(export_data))

        for img in draft.images:
            img_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}", img.filename)
            if os.path.exists(img_path):
                zip.write(img_path, arcname = img.filename)

    return filename

def import_draft(file: FileStorage) -> int | Literal[False]:
    if not current_user.is_authenticated: return False

    os.makedirs(EXPORT_PATH, exist_ok=True)
    filename = get_free_filename(EXPORT_PATH, "zip", "import")
    file.save(os.path.join(EXPORT_PATH, filename))

    with zipfile.ZipFile(os.path.join(EXPORT_PATH, filename), 'r') as zip:
        if 'export.json' not in zip.namelist():
            return False
        
        with zip.open('export.json') as f:
            data = json.load(f)
        
        # Create a new draft
        draft = Draft()
        draft.name = data.get("name", "Imported Draft")
        draft.owner_id = current_user.id
        db.session.add(draft)
        db.session.commit()
        
        draft_upload_path = os.path.join(UPLOAD_PATH, "sets", f"draft_{draft.id}")

        # Extract images and create DraftImage entries
        for img_data in data.get("images", []):
            img_filename = img_data.get("filename")
            img_label = img_data.get("label", "")

            if img_filename in zip.namelist():
                os.makedirs(draft_upload_path, exist_ok=True)
                zip.extract(img_filename, path=draft_upload_path)

                draft_image = DraftImage(draft.id, img_filename, -1, 0, img_label)
                db.session.add(draft_image)
        db.session.commit()

    return draft.id
