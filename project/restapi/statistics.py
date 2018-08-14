from .blueprint import api
from project.models import CategoriesManager
from .schemas import ProductsByCategorySchema


@api.route('/statistics/products_by_category')
def products_by_category():
    result = map(lambda row: dict(category=row[0], count=row[1]),
                 CategoriesManager.count_all_products())
    return ProductsByCategorySchema(many=True).jsonify(result)
