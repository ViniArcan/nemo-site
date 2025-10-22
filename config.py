import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///posts.db')
    UPLOAD_FOLDER = 'static/uploads/'
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_default_secret_key')
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_ROOT = 'posts'
    FLATPAGES_AUTO_RELOAD = True
