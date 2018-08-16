import os

import click
from app import create_app
from flask.cli import FlaskGroup


def create_cli_app():
    return create_app()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
@click.option('--debug', is_flag=True, default=False)
def cli(debug):
    if debug:
        os.environ['FLASK_DEBUG'] = '1'


@cli.command()
def populate_db():
    """ Populates the database with random data """
    import project.tests.factories as factories
    import random
    from project.models import OrderStatusEnum

    countries = factories.CountryFactory.create_batch(10)
    customers = []
    for country in countries:
        customers += factories.CustomerFactory.create_batch(
            random.randint(1, 10), country=country)
    categories = factories.CategoryFactory.create_batch(20)
    tags = factories.TagFactory.create_batch(10)
    products = []
    for _ in range(10):
        products.append(factories.ProductFactory.create(
            category=random.choice(categories),
            tags=[t.name for t in random.sample(tags, random.randint(1, 4))]
        ))
    for _ in range(50):
        order = factories.OrderFactory.create(
            customer=random.choice(customers),
            status=random.choice(list(OrderStatusEnum))
        )
        order_products = random.sample(products, random.randint(1, 5))
        for p in order_products:
            order.add_product(p, random.randint(1, 10))


if __name__ == '__main__':
    cli()
