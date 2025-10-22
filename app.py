from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, bcrypt, User
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

# Security check for default SECRET_KEY in production
if not app.debug and app.config['SECRET_KEY'] == 'a_default_secret_key':
    raise ValueError('A proper SECRET_KEY must be set in the .env file for production.')

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
    return db.session.get(User, user_id)

register_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
