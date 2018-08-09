import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(os.getenv(
    'APP_SETTINGS',
    'project.config.DevelopmentConfig'
))
db = SQLAlchemy(app)
engine = db.engine
ma = Marshmallow(app)
migrate = Migrate(app)



