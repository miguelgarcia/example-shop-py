import factory
from app import models
from app import db

from .factoryboyfixture import make_fixture


@make_fixture()
class CountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Country
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: u'Country %d' % n)


@make_fixture()
class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Category
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: u'Category %d' % n)


@make_fixture()
class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Tag
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: u'Tag %d' % n)


@make_fixture(uses=[TagFactory])
class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Product
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Sequence(lambda n: u'Product %d' % n)
    description = factory.Sequence(lambda n: u'The product %d' % n)
    price = factory.Faker('pydecimal', left_digits=3,
                          right_digits=2, positive=True)
    status = models.ProductStatusEnum.ACTIVE
    category = factory.SubFactory(CategoryFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if extracted is not None:
            self.tags = extracted
            return
        for _ in range(2):
            tag = TagFactory.create()
            self.tags.append(tag.name)


@make_fixture()
class CustomerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Customer
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')
    email = factory.Faker('email')
    country = factory.SubFactory(CountryFactory)


@make_fixture(uses=[ProductFactory])
class OrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Order
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    customer = factory.SubFactory(CustomerFactory)
    status = models.OrderStatusEnum.PENDING

    @factory.post_generation
    def details(self, create, extracted, **kwargs):
        if extracted is not None:
            for _ in range(extracted):
                self.add_product(ProductFactory.create(), 1)
