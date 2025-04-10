from flask import render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from shutil import rmtree
from uuid import uuid4
import json
import os

from lib import *
from db import *
from app import *


@app.route('/')
def index():
    presentations = Presentation.query.all()
    return render_template('index.html', presentations = presentations)



@app.route('/upload', methods = ['POST'])
def upload():
    if 'file' not in request.files: return redirect("/")

    file = request.files['file']
    uuid = uuid4().hex
    upload_file(app.root_path, file, uuid)
    if not uuid: return redirect("/")

    success = extract_images(file, uuid)
    if not success: return redirect("/")
    # if not Presentation.query.filter_by(uuid = uuid).first(): return redirect("/")

    return redirect(f"/set/{uuid}/edit")



@app.route('/set/<string:uuid>/edit')
def edit(uuid: str):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return redirect("/")

    img_count = len(Image.query.filter_by(pres_id = presentation.id).all())
    return render_template('edit.html', uuid = uuid, images_count = img_count, title = presentation.title, images = Image.query.filter_by(pres_id = presentation.id).all())



@app.route('/set/<string:uuid>/image/<int:index>')
def get_image(uuid: str, index: int):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return "Presentation not found"

    images = Image.query.filter_by(pres_id = presentation.id).all()
    
    if index >= len(images) or index < 0: return "Image not found"
    image = images[index]
    image_data = get_image_data(image.file, uuid)

    labels = Label.query.filter_by(pres_id = presentation.id, slide = image.slide).all()

    return json.dumps({"image": image_data, "options": [option.text for option in labels]})



@app.route('/set/<string:uuid>/title', methods = ['POST'])
def edit_title(uuid: str):
    if "title" not in request.form: return ""

    title = request.form["title"]
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    presentation.title = title
    db.session.commit()
    return ""



@app.route("/set/<string:uuid>/save", methods = ['POST'])
def save_presentation(uuid: str):
    if "data" not in request.form: return ""

    titles = json.loads(request.form["data"])
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    images = Image.query.filter_by(pres_id = presentation.id).limit(1)

    presentation.visible = 1

    for i, t in titles.items():
        images.offset(i).first().title = t

    db.session.commit()

    return ""



@app.route('/set/<string:uuid>/delete')
def delete_presentation(uuid: str):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return redirect("/")

    rmtree(os.path.join(UPLOADS_DIR, uuid))
    Presentation.query.filter_by(uuid = uuid).delete()
    Image.query.filter_by(pres_id = presentation.id).delete()
    Label.query.filter_by(pres_id = presentation.id).delete()
    db.session.commit()

    return redirect("/?m=Presentation deleted")



@app.route('/set/<string:uuid>/play')
def play(uuid: str):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return redirect("/")

    images = Image.query.filter_by(pres_id = presentation.id).all()

    return render_template('play.html', presentation = presentation, images = {image.id: image.title for image in images})



@app.route('/clearall')
def clear_all():
    Presentation.query.delete()
    Image.query.delete()
    Label.query.delete()
    db.session.commit()
    rmtree(UPLOADS_DIR, ignore_errors = True)
    os.makedirs(UPLOADS_DIR, exist_ok = True)
    return redirect("/")



if __name__ == '__main__':
    app.run(debug = True)
