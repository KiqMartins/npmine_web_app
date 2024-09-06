from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from websiteNPMINE.config import Config
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap4

db = SQLAlchemy()

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.home'
login_manager.login_message_category = 'info'
bootstrap = Bootstrap4()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    bcrypt.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)

    login_manager.init_app(app)

    from websiteNPMINE.users.routes import users
    from websiteNPMINE.main.routes import main
    from websiteNPMINE.compounds.routes import compounds
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(compounds)

    migrate = Migrate(app,db)


    return app


