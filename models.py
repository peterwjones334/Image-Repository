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
