from flask import jsonify
from marshmallow.exceptions import ValidationError

from .blueprint import api
from .cruds import (CategoriesView, CountriesView, CustomersView, OrdersView,
                    ProductsView)
from . import statistics    # noqa: F401


def register_crud_view(view_class, plural, list_methods=['GET', 'POST'],
                       record_methods=['GET', 'PUT', 'DELETE']):
    """ Register routes endpoints for a CRUD
        /plural
        /plural/<int:id>

        Allowed methods can be configured using list_methods and record_methods
    """
    view = view_class.as_view(plural)
    if 'GET' in list_methods:
        api.add_url_rule('/%s' % plural, defaults={'id': None},
                         view_func=view, methods=['GET', ])
    api.add_url_rule('/%s/<int:id>' % plural, view_func=view,
                     methods=record_methods)
    if 'POST' in list_methods:
        api.add_url_rule('/%s' % plural, view_func=view, methods=['POST', ])


register_crud_view(CategoriesView, 'categories')
register_crud_view(CountriesView, 'countries')
register_crud_view(CustomersView, 'customers')
register_crud_view(ProductsView, 'products')
register_crud_view(OrdersView, 'orders', record_methods=['GET', 'PUT'])


@api.errorhandler(ValidationError)
def schema_violation_exception_handler(error):
    return jsonify({'status': 422, 'message': str(error)}), 422


__all__ = ['api']
