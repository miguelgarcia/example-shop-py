from .blueprint import api
from project.models import ProductsManager, CustomersManager
from .schemas import ProductsByCategorySchema, CustomersByCountrySchema


@api.route('/statistics/products_by_category')
def products_by_category():
    return ProductsByCategorySchema(many=True).jsonify(
        ProductsManager.count_by_category())


@api.route('/statistics/customers_by_country')
def customers_by_country():
    return CustomersByCountrySchema(many=True).jsonify(
        CustomersManager.count_by_country())
