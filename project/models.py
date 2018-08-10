import datetime
import enum

from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from sqlalchemy.sql import label

from project.settings import db

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

class CategoriesManager:
    @staticmethod
    def count_all_products():
        return db.session.query(Category, label('count', func.count(Product.id))).outerjoin(Category.products).group_by(Category.id).order_by(Category.id).all()


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
    orders = db.relationship('Order', backref=db.backref('customer'),
                             lazy='dynamic')

    class CustomerQuery(BaseQuery):
        def filter_country(self, country):
            return self.filter(Customer.country == country)

    query_class = CustomerQuery

    def __repr__(self):
        return '<Customer %r>' % self.email


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


class ProductStatusEnum(enum.Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    COMING_SOON = 'COMING_SOON'


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50), nullable=False, unique=True)
    description = db.Column(db.UnicodeText())
    price = db.Column(db.Numeric(precision=2, asdecimal=True))
    category_id = db.Column(db.Integer, db.ForeignKey(
        'category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref(
        'products', lazy='dynamic'), lazy='select')
    status = db.Column(
        db.Enum(ProductStatusEnum, validate_strings=True), nullable=False)

    tags_rel = db.relationship(
        'Tag', secondary='product_tag', backref='products')
    tags = association_proxy(
        'tags_rel', 'name', creator=lambda name: Tag.query.get_or_create(name=name))
    category_name = association_proxy(
        'category', 'name', creator=lambda name: Category.query.get_or_create(name=name))

    def __repr__(self):
        return '<Product %r>' % self.name

    @hybrid_property
    def sells(self):
        return db.session.query(
            label('count', func.sum(OrderDetail.quantity))
        ).filter(OrderDetail.product == self).scalar()

class ProductsManager:
    @staticmethod
    def sells_by_product():
        return db.session.query(Product, label('sells', func.sum(OrderDetail.quantity))
        ).outerjoin(Product.orders_details).group_by(Product.id).all()

    @staticmethod
    def units_delivered_by_product_by_country():
        return db.session.query(Product, Country, label('units', func.sum(OrderDetail.quantity))
            ).outerjoin(Product.orders_details
            ).outerjoin(OrderDetail.order
            ).outerjoin(Order.customer
            ).filter(Order.status==OrderStatusEnum.DELIVERED
            ).outerjoin(Customer.country
            ).group_by(Product.id, Country.id).all()


class ProductTag(db.Model):
    __tablename__ = 'product_tag'
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    product = db.relationship('Product', backref=db.backref(
        'product_tags', cascade='all, delete-orphan'))
    tag = db.relationship('Tag', backref=db.backref(
        'product_tags', cascade='all, delete-orphan'))


class OrderStatusEnum(enum.Enum):
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
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref(
        'orders_details'), lazy='joined')
    unit_price = db.Column(db.Numeric(precision=2, asdecimal=True))
    quantity = db.Column(db.Integer, nullable=False)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    status = db.Column(
        db.Enum(OrderStatusEnum, validate_strings=True), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self.created_at = datetime.datetime.now()

    @hybrid_property
    def total(self):
        return sum(map(lambda d: d.unit_price * d.quantity, self.detail))

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
        return db.session.query(Order.status, label('count', func.count(Order.id))).group_by(Order.status).all()
