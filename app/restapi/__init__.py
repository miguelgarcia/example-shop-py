from flask import Blueprint, jsonify
from marshmallow.exceptions import ValidationError
from .views import CategoriesView, CountriesView

api = Blueprint('api', __name__)

def register_view(view_class, plural):
    view = view_class.as_view(plural+'_view')
    api.add_url_rule('/%s' % plural, defaults={'id': None},
                    view_func=view, methods=['GET',])
    api.add_url_rule('/%s/<int:id>' % plural, view_func=view,
                    methods=['GET', 'PUT', 'DELETE'])
    api.add_url_rule('/%s' % plural, view_func=view, methods=['POST',])

register_view(CategoriesView, 'categories')
register_view(CountriesView, 'countries')

@api.errorhandler(ValidationError)
def schema_violation_exception_handler(error):
    current_app.logger.error(error)
    return jsonify({'status': 422, 'message': str(error)}), 422

