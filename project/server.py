from project.settings import app, db
from flask import jsonify
from .restapi import api

app.register_blueprint(api, url_prefix='/api')

@app.route('/help', methods=['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@app.cli.command()
def populate_db():
    """ Populates the database with random data """
    import project.tests.factories as factories
    import random
    from project.models import Order, OrderStatusEnum

    categories = factories.category_factory(db.session).create_batch(20)
    customers = factories.customer_factory(db.session).create_batch(30)
    products = []
    products_factory = factories.product_factory(db.session)
    tags = factories.tag_factory(db.session).create_batch(10)
    for _ in range(50):
        products.append(products_factory.create(
            category=random.choice(categories),
            tags=[t.name for t in random.sample(tags, random.randint(1,4))]
        ))
    orders_factory = factories.order_factory(db.session)
    for _ in range(50):
        order = orders_factory.create(
            customer=random.choice(customers),
            status=random.choice(list(OrderStatusEnum))
        )
        order_products = random.sample(products, random.randint(1,5))
        for p in order_products:
            order.add_product(p, random.randint(1,10))
    