from app import ma
from marshmallow import validate, post_load
from app import models


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

    country = ma.Function(deserialize=lambda v: models.Country.query.get(
        v), required=True, validate=[validate.NoneOf([None])])


class ProductSchema(ma.ModelSchema):
    class Meta:
        model = models.Product
        fields = ('id', 'name', 'description', 'price',
                  'category', 'status', 'tags')

    category = ma.Nested(CategorySchema)
    price = ma.Decimal(as_string=True, places=2)
    status = ma.Function(lambda v: v.status.value)
    tags = ma.Function(lambda v: list(v.tags))


class ProductDeserializeSchema(ProductSchema):
    class Meta:
        model = models.Product
        fields = ('name', 'description', 'price', 'category', 'status', 'tags')

    category = ma.Function(deserialize=lambda v: models.Category.query.get(
        v), required=True, validate=[validate.NoneOf([None])])

    status = ma.Function(deserialize=models.ProductStatusEnum.find,
                         required=True,
                         validate=[validate.NoneOf([None])])
    tags = ma.List(ma.String(), required=True)


class OrderDetailSchema(ma.ModelSchema):
    class Meta:
        model = models.OrderDetail
        fields = ('id', 'quantity', 'unit_price', 'product')

    product = ma.Nested(ProductSchema, only=('id', 'name'))
    unit_price = ma.Decimal(as_string=True, places=2)


class OrderSchema(ma.ModelSchema):
    class Meta:
        model = models.Order
        fields = ('id', 'created_at', 'total', 'status', 'customer', 'detail')

    status = ma.Function(lambda v: v.status.value)
    customer = ma.Nested(CustomerSchema, only=(
        'id', 'email', 'firstname', 'lastname'))
    detail = ma.Nested(OrderDetailSchema, many=True)
    total = ma.Decimal(as_string=True, places=2, dump_only=True)


class OrdersListSchema(OrderSchema):
    class Meta:
        model = models.Order
        fields = ('id', 'created_at', 'status',
                  'customer', 'total')

    status = ma.Function(lambda row: row.Order.status.value)

    @staticmethod
    def get_attribute(obj, attr, default):
        if attr == 'total':
            return obj.total
        return getattr(obj.Order, attr, default)


class OrderDetailCreateSchema(ma.Schema):
    product = ma.Function(deserialize=lambda v: models.Product.query.get(
        v), required=True, validate=[validate.NoneOf([None])])
    quantity = ma.Integer(required=True, validate=[validate.Range(1)])


class OrderCreateSchema(ma.Schema):
    customer = ma.Function(deserialize=lambda v: models.Customer.query.get(
        v), required=True, validate=[validate.NoneOf([None])])
    detail = ma.Nested(OrderDetailCreateSchema, many=True)

    @post_load
    def create_order(self, data):
        order = models.Order(customer=data['customer'])
        for detail in data['detail']:
            order.add_product(detail['product'], detail['quantity'])
        return order


class OrderUpdateSchema(ma.ModelSchema):
    class Meta:
        model = models.Order
        fields = ('status',)

    status = ma.Function(deserialize=models.OrderStatusEnum.find,
                         required=True,
                         validate=[validate.NoneOf([None])])

# Statistics schemas


class ProductsByCategorySchema(ma.Schema):
    category = ma.Nested(CategorySchema)
    count = ma.Integer()


class CustomersByCountrySchema(ma.Schema):
    country = ma.Nested(CountrySchema)
    count = ma.Integer()


class OrdersByStatusSchema(ma.Schema):
    count = ma.Integer()
    status = ma.Function(lambda row: row.status.value)


class SellsByProductSchema(ma.Schema):
    product = ma.Nested(ProductSchema)
    sells = ma.Integer()


class UnitsDeliveredByProductByCountrySchema(ma.Schema):
    product_name = ma.String()
    product_id = ma.Integer()
    country_name = ma.String()
    country_id = ma.Integer()
    units = ma.Integer()
