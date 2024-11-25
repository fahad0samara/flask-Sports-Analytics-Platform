from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.predictions import bp as predictions_bp
    app.register_blueprint(predictions_bp, url_prefix='/predictions')

    # Register context processors
    @app.context_processor
    def utility_processor():
        return {
            'now': datetime.utcnow
        }

    return app

from app import models

@login.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))
