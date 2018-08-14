import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv(
            'APP_SETTINGS',
            'project.config.DevelopmentConfig'
        )
    app = Flask(__name__)
    app.config.from_object(config_name)
    init_extensions(app)
    register_blueprints(app)
    return app


def init_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    from project.restapi import api
    app.register_blueprint(api, url_prefix='/api')
