from flask import render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from shutil import rmtree
import json
from lib import *


@app.route('/')
def index():
    presentations = Presentation.query.all()
    return render_template('index.html', presentations = presentations)



@app.route('/upload', methods = ['POST'])
def upload():
    if 'file' not in request.files: return redirect("/")

    file = request.files['file']
    uuid = upload_file(app.root_path, file)
    if not uuid: return redirect("/")

    success = extract_images(file, uuid)
    if not success: return redirect("/")
    # if not Presentation.query.filter_by(uuid = uuid).first(): return redirect("/")

    return redirect(f"/edit/{uuid}")



@app.route('/edit/<string:uuid>')
def edit(uuid: str):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return redirect("/")

    img_count = len(Image.query.filter_by(presentation = presentation.id).all())
    return render_template('edit.html', uuid = uuid, images_count = img_count, title = presentation.title)



@app.route('/getimage/<string:uuid>/<int:index>')
def get_image(uuid: str, index: int):
    presentation = Presentation.query.filter_by(uuid = uuid).first()
    if not isinstance(presentation, Presentation): return "Presentation not found"

    images = Image.query.filter_by(presentation = presentation.id).all()
    
    if index >= len(images) or index < 0: return "Image not found"
    image = images[index]
    image_data = get_image_data(image.file, uuid)

    labels = Label.query.filter_by(presentation = presentation.id, slide = image.slide).all()

    return json.dumps({"image": image_data, "options": [option.text for option in labels]})



@app.route('/clearall')
def clear_all():
    Presentation.query.delete()
    Image.query.delete()
    Label.query.delete()
    db.session.commit()
    rmtree(os.path.join(app.root_path, "user_upload"))
    os.makedirs(os.path.join(app.root_path, "user_upload"))
    return redirect("/")



if __name__ == '__main__':
    app.run(debug = True)