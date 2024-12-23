from . import db
from flask_login import UserMixin

class book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    cover_image_url = db.Column(db.String(255), nullable=True)  # URL к фото обложки
    
class useradmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password