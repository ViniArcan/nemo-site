from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
import uuid

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text, nullable=True)
    profile_image_path = db.Column(db.String(255), nullable=True, default='static/uploads/default_avatar.png')

    def __init__(self, email:str, password:str, name:str):
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.name = name

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
