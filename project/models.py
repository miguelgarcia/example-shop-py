import datetime
import decimal
import enum

from flask_sqlalchemy import BaseQuery
from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import label

from project.app import db


class ModelEnum(enum.Enum):
    @classmethod
    def find(cls, name):
        if name in cls.__members__:
            return cls[name]
        return None


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name

    def products_count(self):
        return self.products.count()

    class CategoryQuery(BaseQuery):
        def get_or_create(self, name):
            with db.session.no_autoflush:
                category = Category.query.filter(Category.name == name).first()
                if category is None:
                    category = Category(name=name)
            return category

    query_class = CategoryQuery


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)

    def __repr__(self):
        return '<Country %r>' % self.name


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.Unicode(30), nullable=False)
    lastname = db.Column(db.Unicode(30), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey(
        'country.id'), nullable=False)
    country = db.relationship('Country', backref='customers')
    orders = db.relationship(
        'Order',
        backref=db.backref('customer', lazy='joined'),
        lazy='dynamic'
    )

    class CustomerQuery(BaseQuery):
        def filter_country(self, country):
            return self.filter(Customer.country == country)

    query_class = CustomerQuery

    def __repr__(self):
        return '<Customer %r>' % self.email


class CustomersManager:
    @staticmethod
    def count_by_country():
        country = aliased(Country, name='country')
        return (
            db.session.query(
                country,
                label('count', func.count(Customer.id))
            )
            .outerjoin(country.customers)
            .group_by(country.id)
            .order_by(country.id)
            .all()
        )


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)

    def __repr__(self):
        return '<Tag %r>' % self.name

    class TagQuery(BaseQuery):
        def get_or_create(self, name):
            with db.session.no_autoflush:
                tag = Tag.query.filter(Tag.name == name).first()
                if tag is None:
                    tag = Tag(name=name)
            return tag

    query_class = TagQuery


class ProductStatusEnum(ModelEnum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    COMING_SOON = 'COMING_SOON'


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)
    description = db.Column(db.UnicodeText())
    price = db.Column(db.Numeric(10, 5, asdecimal=True))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            nullable=False)
    category = db.relationship('Category', backref=db.backref(
        'products', lazy='dynamic'), lazy='select')
    status = db.Column(
        db.Enum(ProductStatusEnum, validate_strings=True),
        nullable=False
    )
    rel_tags = db.relationship('Tag', secondary='product_tag',
                               backref='products')
    tags = association_proxy(
        'rel_tags', 'name',
        creator=lambda name: Tag.query.get_or_create(name=name)
    )
    category_name = association_proxy(
        'category', 'name',
        creator=lambda name: Category.query.get_or_create(name=name)
    )

    def __repr__(self):
        return '<Product %r>' % self.name

    @hybrid_property
    def sells(self):
        return (
            db.session.query(label('count', func.sum(OrderDetail.quantity)))
            .filter(OrderDetail.product == self).scalar()
        )

    @sells.expression
    def sells(cls):
        return (
            select([func.coalesce(func.sum(
                OrderDetail.quantity), 0
            )])
            .where(OrderDetail.product_id == cls.id)
            .label('sells')
        )


class ProductsManager:
    @staticmethod
    def sells_by_product():
        """ Returns a list of (product, sells) """
        product = aliased(Product, name='product')
        return db.session.query(product, product.sells).all()
        # The next code does the same but uses join instead subquery
        # return (
        #     db.session.query(
        #         product,
        #         label('sells',
        #               func.coalesce(func.sum(OrderDetail.quantity), 0))
        #     )
        #     .outerjoin(product.orders_details).group_by(product.id).all()
        # )

    @staticmethod
    def units_delivered_by_product_by_country():
        """ Returns a list a of (product, country, units)
            containing the amount of units delivered to each country for each
            product
        """
        product = aliased(Product, name='product')
        country = aliased(Customer.country, name='country')
        q = (
            db.session.query(
                label('product_name', product.name),
                label('product_id', product.id),
                label('country_name', country.name),
                label('country_id', country.id),
                label('units', func.sum(OrderDetail.quantity))
            )
            .outerjoin(product.orders_details)
            .outerjoin(OrderDetail.order)
            .outerjoin(Order.customer)
            .outerjoin(country)
            .filter(Order.status == OrderStatusEnum.DELIVERED)
            .group_by(product.id, country.id))
        return q.all()

    @staticmethod
    def count_by_category():
        """ Count how many products are in each category """
        category = aliased(Category, name='category')
        return (
            db.session.query(
                category,
                label('count', func.count(Product.id))
            )
            .outerjoin(category.products)
            .group_by(category.id)
            .order_by(category.id)
            .all()
        )


class ProductTag(db.Model):
    __tablename__ = 'product_tag'
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)


class OrderStatusEnum(ModelEnum):
    PENDING = 'PENDING'
    PAYED = 'PAYED'
    SHIPPING = 'SHIPPING'
    DELIVERED = 'DELIVERED'
    CANCELED = 'CANCELED'


class OrderDetail(db.Model):
    __tablename__ = 'order_detail'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    order = db.relationship('Order', backref='detail')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'),
                           nullable=False)
    product = db.relationship('Product', backref=db.backref('orders_details'),
                              lazy='joined')
    unit_price = db.Column(db.Numeric(10, 5, asdecimal=True))
    quantity = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def total(self):
        return decimal.Decimal(self.unit_price * self.quantity)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'),
                            nullable=False)
    status = db.Column(db.Enum(OrderStatusEnum, validate_strings=True),
                       nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self.created_at = datetime.datetime.now()
        if 'status' not in kw:
            self.status = OrderStatusEnum.PENDING

    @hybrid_property
    def total(self):
        return decimal.Decimal(sum(map(lambda d: d.total, self.detail)))

    @total.expression
    def total(cls):
        return (
            select([func.coalesce(func.sum(
                OrderDetail.unit_price * OrderDetail.quantity), 0
            )])
            .where(OrderDetail.order_id == cls.id)
            .label('total')
        )

    def add_product(self, product, quantity):
        self.detail.append(OrderDetail(
            product=product,
            quantity=quantity,
            unit_price=product.price
        ))

    def __repr__(self):
        return '<Order %r>' % self.id


class OrdersManager:
    @staticmethod
    def count_by_status():
        """ Returns a list of (OrderStatusEnum, count) containing how many
            orders are currently in each state
        """
        return db.session.query(
                label('status', Order.status),
                label('count', func.count(Order.id))
            ).group_by(Order.status).all()
