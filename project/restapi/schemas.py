from project.settings import ma
from marshmallow import validate
from project import models

class ListArgsSchema(ma.Schema):
    limit = ma.Integer(required=False, validate=[
                           validate.Range(1, 100)], missing=100)
    offset = ma.Integer(required=False, validate=[
                            validate.Range(0)], missing=0)

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = models.Category
        fields = ('id', 'name')

class CountrySchema(ma.ModelSchema):
    class Meta:
        model = models.Country
        fields = ('id', 'name')

class CustomerSchema(ma.ModelSchema):
    class Meta:
        model = models.Customer
        fields = ('id', 'email', 'firstname', 'lastname', 'country')

    country = ma.Nested(CountrySchema)

class CustomerDeserializeSchema(CustomerSchema):
    class Meta:
        model = models.Customer
        fields = ('email', 'firstname', 'lastname', 'country')

    country = ma.Function(deserialize=lambda v: models.Country.query.get(v), required=True, validate=[validate.NoneOf([None])])

class ProductSchema(ma.ModelSchema):
    class Meta:
        model = models.Product
        fields = ('id', 'name', 'description', 'price', 'category', 'status', 'tags')

    category = ma.Nested(CategorySchema)
    price = ma.Decimal(as_string=True,places=2)
    status = ma.Function(lambda v: v.status.value)
    tags = ma.Function(lambda v: list(v.tags))

class ProductDeserializeSchema(ProductSchema):
    class Meta:
        model = models.Product
        fields = ('name', 'description', 'price', 'category', 'status', 'tags')

    category = ma.Function(deserialize=lambda v: models.Category.query.get(v), required=True, validate=[validate.NoneOf([None])])
    status = ma.Function(deserialize=lambda v: models.ProductStatusEnum[v] if v in models.ProductStatusEnum.__members__ else None, required=True, validate=[validate.NoneOf([None])])
    tags = ma.List(ma.String())
