import logging
import os

from flask import jsonify
from app.database import db

import app.models

from .factory import create_app

logger = logging.getLogger(__name__)


app_settings = os.getenv(
    'APP_SETTINGS',
    'app.config.DevelopmentConfig'
)

app = create_app(app_settings)

@app.route('/help', methods=['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

from flask import Flask

@app.cli.command()
def populate_db():
    """ Populates the database with generated data """
    import app.tests.factories as factories
    factories.category_factory(db.session).create_batch(10)