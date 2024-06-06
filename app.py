from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from flask_migrate import Migrate
from config import Config
from models import db, ImageMetadata
from forms import UploadForm
import os
import re
from unicodedata import normalize
import uuid

def secure_filename(filename):
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
    _windows_device_files = {
        'CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL',
    }

    if isinstance(filename, str):
        filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_ascii_strip_re.sub('', '_'.join(filename.split()))).strip('._')
    if os.name == 'nt' and filename and filename.split('.')[0].upper() in _windows_device_files:
        filename = f'_{filename}'
    return filename

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    images = ImageMetadata.query.all()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        image_file.save(save_path)
        image = ImageMetadata(
            uid=str(uuid.uuid4()),
            filename=filename,
            part_number=form.part_number.data,
            version=form.version.data,
            owner=form.owner.data,
            category=form.category.data,
            marking=form.marking.data
        )
        db.session.add(image)
        db.session.commit()
        flash('Image successfully uploaded and metadata saved!', 'success')
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)

@app.route('/browse')
def browse():
    query = request.args.get('query')
    if query:
        images = ImageMetadata.query.filter(ImageMetadata.part_number.contains(query) |
                                            ImageMetadata.version.contains(query)).all()
    else:
        images = ImageMetadata.query.all()
    return render_template('browse.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view_image/<filename>')
def view_image(filename):
    return render_template('view_image.html', filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
