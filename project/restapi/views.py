from project.models import Category, Country, Customer, Product

from .crudview import CrudView
from .schemas import (CategorySchema, CountrySchema, CustomerDeserializeSchema,
                      CustomerSchema, ProductDeserializeSchema, ProductSchema)


class CategoriesView(CrudView):
    class Meta:
        model = Category
        get_schema = CategorySchema
        list_schema = CategorySchema

        def post_schema(): return CategorySchema(exclude=('id',))

        def put_schema(): return CategorySchema(exclude=('id',))


class CountriesView(CrudView):
    class Meta:
        model = Country
        get_schema = CountrySchema
        list_schema = CountrySchema

        def post_schema(): return CountrySchema(exclude=('id',))

        def put_schema(): return CountrySchema(exclude=('id',))


class CustomersView(CrudView):
    class Meta:
        model = Customer
        get_schema = CustomerSchema
        list_schema = CustomerSchema
        post_schema = CustomerDeserializeSchema
        put_schema = CustomerDeserializeSchema

class ProductsView(CrudView):
    class Meta:
        model = Product
        get_schema = ProductSchema
        list_schema = ProductSchema
        post_schema = ProductDeserializeSchema
        put_schema = ProductDeserializeSchema
