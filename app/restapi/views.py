from app.database import db
from app.models import Category, Country

from .crudview import CrudView
from .schemas import CategorySchema, CountrySchema


class CategoriesView(CrudView):
    class Meta:
        model = Category
        get_schema = CategorySchema
        list_schema = CategorySchema
        post_schema = lambda: CategorySchema(exclude=('id',))
        put_schema = lambda: CategorySchema(exclude=('id',))
        db = db

class CountriesView(CrudView):
    class Meta:
        model = Country
        get_schema = CountrySchema
        list_schema = CountrySchema
        post_schema = lambda: CountrySchema(exclude=('id',))
        put_schema = lambda: CountrySchema(exclude=('id',))
        db = db
