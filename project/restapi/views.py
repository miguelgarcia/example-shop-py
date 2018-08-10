from project.models import Category, Country, Customer

from .crudview import CrudView
from .schemas import CategorySchema, CountrySchema, CustomerSchema, CustomerSchemaDeserialize


class CategoriesView(CrudView):
    class Meta:
        model = Category
        get_schema = CategorySchema
        list_schema = CategorySchema
        post_schema = lambda: CategorySchema(exclude=('id',))
        put_schema = lambda: CategorySchema(exclude=('id',))

class CountriesView(CrudView):
    class Meta:
        model = Country
        get_schema = CountrySchema
        list_schema = CountrySchema
        post_schema = lambda: CountrySchema(exclude=('id',))
        put_schema = lambda: CountrySchema(exclude=('id',))

class CustomersView(CrudView):
    class Meta:
        model = Customer
        get_schema = CustomerSchema
        list_schema = CustomerSchema
        post_schema = CustomerSchemaDeserialize
        put_schema = CustomerSchemaDeserialize
