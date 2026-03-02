
from typing import Literal

from app.app import UPLOAD_PATH, EXPORT_PATH
from app.lib.presentation import get_free_filename
from app.models import Draft

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
