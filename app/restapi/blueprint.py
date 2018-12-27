from flask import Blueprint

# This module is separated from __init__ to avoid circular imports

api = Blueprint('api', 'restapi')
