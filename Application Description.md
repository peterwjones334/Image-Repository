## Flask Application Document

Below is a detailed documentation for each component of the Flask application, including the purpose and functionality of each file and key sections of code.

---

### Project Structure

```
Image-Repository-project/
├── app.py
├── config.py
├── forms.py
├── models.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── upload.html
│   ├── browse.html
│   ├── help.html
│   ├── view_image.html
└── uploads/
```

### `app.py`
The main application file that initializes the Flask app, configures it, sets up the database, and defines the routes.

```python
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash
from config import Config
from models import db, ImageMetadata
from forms import UploadForm
import os
import re
from unicodedata import normalize
import uuid

# Function to sanitize filenames
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

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Home page route displaying all uploaded images and metadata
@app.route('/')
def index():
    images = ImageMetadata.query.all()
    return render_template('index.html', images=images)

# Upload page route handling image uploads and metadata submission
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

# Browse page route for searching and displaying images based on metadata
@app.route('/browse')
def browse():
    query = request.args.get('query')
    if query:
        images = ImageMetadata.query.filter(ImageMetadata.part_number.contains(query) |
                                            ImageMetadata.version.contains(query)).all()
    else:
        images = ImageMetadata.query.all()
    return render_template('browse.html', images=images)

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to view image in a new window with a download option
@app.route('/view_image/<filename>')
def view_image(filename):
    return render_template('view_image.html', filename=filename)

# Route to download an image file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Help page route
@app.route('/help')
def help():
    return render_template('help.html')

# Initialize and run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### `config.py`
Configuration file for setting up the Flask app with necessary configurations like secret key, database URI, and upload folder.

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_PATH = 16 * 1024 * 1024  # 16 MB max file size
```

### `forms.py`
Defines the forms used in the application, including the `UploadForm` for uploading images and metadata.

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, ValidationError

# Validator to ensure only allowed image formats are uploaded
def validate_image(form, field):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in field.data.filename or field.data.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        raise ValidationError('Invalid file extension. Allowed extensions are png, jpg, jpeg, gif.')

class UploadForm(FlaskForm):
    image = FileField('Image', validators=[DataRequired(), validate_image])
    part_number = StringField('Part Number', validators=[DataRequired()])
    version = StringField('Version', validators=[DataRequired()])
    owner = SelectField('Owner', choices=[('owner1', 'Owner 1'), ('owner2', 'Owner 2'), ('owner3', 'Owner 3')], validators=[DataRequired()])
    category = SelectField('Category', choices=[('cat1', 'Category 1'), ('cat2', 'Category 2'), ('cat3', 'Category 3')], validators=[DataRequired()])
    marking = SelectField('Marking', choices=[('mark1', 'Marking 1'), ('mark2', 'Marking 2'), ('mark3', 'Marking 3')], validators=[DataRequired()])
    submit = SubmitField('Upload')
```

### `models.py`
Defines the database models used in the application, including the `ImageMetadata` model for storing image metadata.

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class ImageMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    filename = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    part_number = db.Column(db.String(120), nullable=False)
    version = db.Column(db.String(120), nullable=False)
    owner = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    marking = db.Column(db.String(120), nullable=False)
```

### Templates

#### `base.html`
Base template for the application, containing the navigation bar and a block for content.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Image Upload App</title>
  </head>
  <body>
    <nav>
      <a href="{{ url_for('index') }}">Home</a> |
      <a href="{{ url_for('upload') }}">Upload</a> |
      <a href="{{ url_for('browse') }}">Browse</a> |
      <a href="{{ url_for('help') }}">Help</a>
    </nav>
    <div>
      {% block content %}{% endblock %}
    </div>
  </body>
</html>
```

#### `index.html`
Displays a list of all uploaded images and their metadata.

```html
{% extends "base.html" %}
{% block content %}
<h1>Image Index</h1>
<ul>
  {% for image in images %}
  <li>
    <a href="{{ url_for('view_image', filename=image.filename) }}" target="_blank">{{ image.filename }}</a>
    ({{ image.date }}) - Part Number: {{ image.part_number }}, Version: {{ image.version }},
    Owner: {{ image.owner }}, Category: {{ image.category }}, Marking: {{ image.marking }}, UID: {{ image.uid }}
  </li>
  {% endfor %}
</ul>
{% endblock %}
```

#### `upload.html`
Form for uploading images and their metadata.

```html
{% extends "base.html" %}
{% block content %}
<h1>Upload Image</h1>
<form method="POST" enctype="multipart/form-data">
  {{ form.hidden_tag() }}
  <p>
    {{ form.image.label }}<br>
    {{ form.image }}
  </p>
  <p>
    {{ form.part_number.label }}<br>
    {{ form.part_number }}
  </p>
  <p>
    {{ form.version.label }}<br>
    {{ form.version }}
  </p>
  <p>
    {{ form.owner.label }}<br>
    {{ form.owner }}
  </p>
  <p>
   

 {{ form.category.label }}<br>
    {{ form.category }}
  </p>
  <p>
    {{ form.marking.label }}<br>
    {{ form.marking }}
  </p>
  <p>{{ form.submit }}</p>
</form>
{% endblock %}
```

#### `browse.html`
Form and list for browsing and searching images based on metadata.

```html
{% extends "base.html" %}
{% block content %}
<h1>Browse Images</h1>
<form method="GET">
  <input type="text" name="query" placeholder="Search...">
  <input type="submit" value="Search">
</form>
<ul>
  {% for image in images %}
  <li>
    <a href="{{ url_for('view_image', filename=image.filename) }}" target="_blank">{{ image.filename }}</a>
    ({{ image.date }}) - Part Number: {{ image.part_number }}, Version: {{ image.version }},
    Owner: {{ image.owner }}, Category: {{ image.category }}, Marking: {{ image.marking }}, UID: {{ image.uid }}
  </li>
  {% endfor %}
</ul>
{% endblock %}
```

#### `help.html`
Help page providing instructions on how to use the application.

```html
{% extends "base.html" %}
{% block content %}
<h1>Help Page</h1>
<p>Welcome to the Image Upload Application. Here is how you can use the application:</p>

<h2>Uploading Images</h2>
<ol>
    <li>Navigate to the <a href="{{ url_for('upload') }}">Upload</a> page.</li>
    <li>Fill in the form with the required metadata:
        <ul>
            <li><strong>Image</strong>: Choose the image file you want to upload. Allowed formats are png, jpg, jpeg, gif.</li>
            <li><strong>Part Number</strong>: Enter the part number associated with the image.</li>
            <li><strong>Version</strong>: Enter the version of the image.</li>
            <li><strong>Owner</strong>: Select the owner from the dropdown list.</li>
            <li><strong>Category</strong>: Select the category from the dropdown list.</li>
            <li><strong>Marking</strong>: Select the marking from the dropdown list.</li>
        </ul>
    </li>
    <li>Click the "Upload" button to upload the image and save the metadata. Each uploaded image will be assigned a unique identifier (UID).</li>
</ol>

<h2>Browsing Images</h2>
<ol>
    <li>Navigate to the <a href="{{ url_for('browse') }}">Browse</a> page.</li>
    <li>Enter a query in the search bar to filter images based on part number, version, owner, category, marking, or leave it empty to see all images.</li>
    <li>Click on the filename link to view the image in a new window. In the new window, you can see the image and download it using the "Download" button.</li>
</ol>

<h2>Viewing Image Index</h2>
<ol>
    <li>Navigate to the <a href="{{ url_for('index') }}">Home</a> page.</li>
    <li>See a list of all uploaded images along with their metadata including the UID.</li>
</ol>

<h2>Image Metadata</h2>
<p>Each image uploaded to the application will have the following metadata fields:</p>
<ul>
    <li><strong>UID</strong>: A unique identifier for the image.</li>
    <li><strong>Filename</strong>: The name of the uploaded file.</li>
    <li><strong>Date</strong>: The upload date of the image.</li>
    <li><strong>Part Number</strong>: The part number associated with the image.</li>
    <li><strong>Version</strong>: The version of the image.</li>
    <li><strong>Owner</strong>: The owner of the image, selected from a dropdown list.</li>
    <li><strong>Category</strong>: The category of the image, selected from a dropdown list.</li>
    <li><strong>Marking</strong>: The marking of the image, selected from a dropdown list.</li>
</ul>

<p>If you have any questions or need further assistance, please contact support.</p>
{% endblock %}
```

#### `view_image.html`
Displays the selected image with an option to download it.

```html
{% extends "base.html" %}
{% block content %}
<h1>View Image</h1>
<img src="{{ url_for('uploaded_file', filename=filename) }}" alt="{{ filename }}" style="max-width: 100%;">
<br>
<a href="{{ url_for('download_file', filename=filename) }}" class="btn btn-primary">Download</a>
{% endblock %}
```

### requirements.txt

```plaintext
Flask==2.0.3
Flask-SQLAlchemy==2.5.1
WTForms==2.3.3
Flask-WTF==1.0.0
Flask-Migrate==3.1.0
gunicorn==20.1.0
```

### Instructions to Generate the `requirements.txt`

If you already have the dependencies installed in your virtual environment, you can generate the `requirements.txt` file using the following command:

```bash
pip freeze > requirements.txt
```

### Explanation of Each Dependency

- **Flask**: The main framework for the web application.
- **Flask-SQLAlchemy**: SQLAlchemy support for Flask, to handle the database operations.
- **WTForms**: A library for handling forms in Python.
- **Flask-WTF**: Flask integration for WTForms, providing easy form handling and validation.
- **Flask-Migrate**: Handles database migrations for Flask applications using Alembic.
- **gunicorn**: A WSGI HTTP Server for Python, used for deploying the application in production.

### Deployment Steps 

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. **Set Up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   ```bash
   touch .env
   ```

   Add the following content to the `.env` file (adjust as needed):
   ```bash
   FLASK_APP=app.py
   FLASK_ENV=production
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=sqlite:///site.db
   UPLOAD_FOLDER=uploads
   ```

5. **Initialize the Database:**
   ```bash
   flask db init  # Only needed if this is the first migration
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

6. **Run the Application:**
   ```bash
   flask run
   ```

7. **Deploy Using Gunicorn:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

8. **Nginx Configuration for Reverse Proxy:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static {
           alias /path/to/your-repo-name/static;
       }

       location /uploads {
           alias /path/to/your-repo-name/uploads;
       }
   }
   ```

Following these steps and using the `requirements.txt` file provided will help you deploy and run your Flask application smoothly.

###  Secure the Application

For a secure deployment, consider the following steps:

**Use HTTPS**: Obtain and install an SSL certificate (e.g., using Let's Encrypt).
**Set Up a Firewall**: Configure firewall rules to allow traffic on necessary ports.
**Environment Variables**: Ensure sensitive information is kept secure, using environment variables and secure storage.

### Summary
This documentation provides a detailed overview of the Flask application, including the purpose and functionality of each component, deployment instructions, and additional steps for securing the application.