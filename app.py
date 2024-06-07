from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash, send_file, jsonify
from config import Config
from models import db, ImageMetadata
from forms import UploadForm
import os
import re
from unicodedata import normalize
import uuid
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if filename.lower().endswith('.tiff') or filename.lower().endswith('.tif'):
        with Image.open(file_path) as img:
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/png')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view_image/<filename>')
def view_image(filename):
    return render_template('view_image.html', filename=filename)

@app.route('/transform_image', methods=['POST'])
def transform_image():
    data = request.get_json()
    filename = data['filename']
    zoom = data['zoom']
    x_offset = data['x_offset']
    y_offset = data['y_offset']
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)
    
    width, height = image.size
    image = image.resize((int(width * zoom), int(height * zoom)), Image.LANCZOS)
    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/download_image', methods=['POST'])
def download_image():
    data = request.get_json()
    filename = data['filename']
    format = data['format']
    base_filename, _ = os.path.splitext(filename)
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(image_path)

    if format.lower() == 'pdf':
        img_io = BytesIO()
        if image.width > image.height:
            page_size = landscape(A4)
        else:
            page_size = A4
        pdf_canvas = canvas.Canvas(img_io, pagesize=page_size)
        width, height = page_size
        image_aspect = image.width / image.height
        page_aspect = width / height
        if image_aspect > page_aspect:
            # Fit to width
            scale = width / image.width
        else:
            # Fit to height
            scale = height / image.height
        scaled_width = image.width * scale
        scaled_height = image.height * scale
        pdf_canvas.drawImage(image_path, 0, height - scaled_height, width=scaled_width, height=scaled_height)
        pdf_canvas.showPage()
        pdf_canvas.save()
        img_io.seek(0)
        return send_file(img_io, mimetype='application/pdf', as_attachment=True, download_name=f'{base_filename}.pdf')
    
    img_io = BytesIO()
    if format.lower() == 'jpeg':
        image = image.convert('RGB')
    image.save(img_io, format.upper())
    img_io.seek(0)
    return send_file(img_io, mimetype=f'image/{format}', as_attachment=True, download_name=f'{base_filename}.{format}')

@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
