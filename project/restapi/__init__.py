from flask import Blueprint, jsonify
from marshmallow.exceptions import ValidationError

from project.settings import db

from .views import (CategoriesView, CountriesView, CustomersView, OrdersView,
                    ProductsView)

api = Blueprint('api', __name__)

def register_crud_view(view_class, plural, list_methods=['GET', 'POST'], record_methods=['GET', 'PUT', 'DELETE']):
    view = view_class.as_view(plural+'_view', session=db.session)
    if 'GET' in list_methods:
        api.add_url_rule('/%s' % plural, defaults={'id': None},
                    view_func=view, methods=['GET',])
    api.add_url_rule('/%s/<int:id>' % plural, view_func=view,
                    methods=record_methods)
    if 'POST' in list_methods:
        api.add_url_rule('/%s' % plural, view_func=view, methods=['POST',])

register_crud_view(CategoriesView, 'categories')
register_crud_view(CountriesView, 'countries')
register_crud_view(CustomersView, 'customers')
register_crud_view(ProductsView, 'products')
register_crud_view(OrdersView, 'orders', record_methods=['GET', 'PUT'])

@api.errorhandler(ValidationError)
def schema_violation_exception_handler(error):
    return jsonify({'status': 422, 'message': str(error)}), 422
