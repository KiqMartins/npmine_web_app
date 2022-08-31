from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from websiteNPMINE.config import Config
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.home'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    bcrypt.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    from websiteNPMINE.users.routes import users
    from websiteNPMINE.main.routes import main
    from websiteNPMINE.inserts.routes import inserts
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(inserts)

    migrate = Migrate(app,db)

    return app
