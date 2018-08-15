from project.models import CustomersManager, OrdersManager, ProductsManager

from .blueprint import api
from .schemas import (CustomersByCountrySchema, OrdersByStatusSchema,
                      ProductsByCategorySchema, SellsByProductSchema)


@api.route('/statistics/products_by_category')
def products_by_category():
    return ProductsByCategorySchema(many=True).jsonify(
        ProductsManager.count_by_category())


@api.route('/statistics/customers_by_country')
def customers_by_country():
    return CustomersByCountrySchema(many=True).jsonify(
        CustomersManager.count_by_country())


@api.route('/statistics/orders_by_status')
def orders_by_status():
    return OrdersByStatusSchema(many=True).jsonify(
        OrdersManager.count_by_status())


@api.route('/statistics/sells_by_product')
def sells_by_product():
    return SellsByProductSchema(many=True).jsonify(
        ProductsManager.sells_by_product())
