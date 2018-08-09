from flask import Flask
from app.database import db, migrate
from app.marshmallow import ma
from app.restapi import api
    
def create_app(config):
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config)
    register_extensions(app)
    app.register_blueprint(api, url_prefix='/api')
    return app

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

