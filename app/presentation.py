
import os.path

from typing import Literal
from werkzeug.datastructures import FileStorage
from pptx.enum.shapes import MSO_SHAPE_TYPE as SHAPE_TYPE
from pptx import Presentation

from app.app import UPLOAD_PATH

TEMP_UPLOAD_PATH = os.path.join(UPLOAD_PATH, "temp")


def extract_images(presentation_file: FileStorage) -> bool:
    address = temp_save(presentation_file)
    if not address: return False

    print("Presentation file:", presentation_file, "Temporary address:", address)
    prs = Presentation(address)

    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.shape_type == SHAPE_TYPE.PICTURE: continue
            
    
    return True


def temp_save(file: FileStorage) -> str | Literal[False]:
    if file.filename is None: return False

    EXTENSION = file.filename.rsplit('.', 1)[-1].lower()
    FILENAME = get_free_filename(TEMP_UPLOAD_PATH, EXTENSION)
    path = os.path.join(TEMP_UPLOAD_PATH, FILENAME)

    file.save(path)
    return path


def temp_remove(file_path: str) -> bool:
    if not os.path.exists(file_path): return False
    os.remove(file_path)
    return True


def get_free_filename(dir: str, ext: str) -> str:
    counter = 0
    while True:
        counter += 1
        path = os.path.join(dir, f"tmp_{counter:0>6}.{ext}")
        if not os.path.exists(path): return path
