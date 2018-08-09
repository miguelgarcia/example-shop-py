import logging
import os
from project.settings import app, db, ma, migrate
from flask import jsonify
import project.models
from .restapi import api
logger = logging.getLogger(__name__)

app.register_blueprint(api, url_prefix='/api')
print("server")
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
    import project.tests.factories as factories
    factories.category_factory(db.session).create_batch(10)