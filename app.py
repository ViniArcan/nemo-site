from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, bcrypt, User
from routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

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
