import random

from project.models import (Customer, CustomersManager, OrdersManager,
                            OrderStatusEnum, ProductsManager)
from sqlalchemy.exc import IntegrityError


def test_count_customers_by_country(customer_factory, country_factory):
    """ Test counting customers in all countries """
    counts = [random.randint(0, 10) for _ in range(10)]
    countries = country_factory.create_batch(len(counts))
    for i in range(len(counts)):
        customer_factory.create_batch(counts[i], country=countries[i])
    expected = [(countries[i], counts[i]) for i in range(len(counts))]
    calc = CustomersManager.count_by_country()
    assert expected == calc


def test_products_count_by_category(product_factory, category_factory):
    """ Test counting products in all categories """
    counts = [random.randint(0, 10) for _ in range(10)]
    categories = category_factory.create_batch(len(counts))
    for i in range(len(counts)):
        product_factory.create_batch(counts[i], category=categories[i])
    expected = [(categories[i], counts[i]) for i in range(len(counts))]
    calc = ProductsManager.count_by_category()
    assert expected == calc


def test_filter_customers_by_country(country_factory, customer_factory):
    """ Test customer query filter by country """
    country1 = country_factory.create()
    country2 = country_factory.create()
    customers1 = customer_factory.create_batch(5, country=country1)
    customer_factory.create_batch(10, country=country2)
    result = Customer.query.filter_country(
        country1).order_by(Customer.id).all()
    assert customers1 == result


def test_customer_email_unique(customer_factory):
    """ Test customer email must be unique"""
    try:
        customer_factory.create_batch(2, email='customer@example.com')
    except IntegrityError:
        return
    assert False


def test_order_total(order_factory, product_factory):
    """ Test order total calculation """
    order = order_factory.create()
    product1 = product_factory.create(price=10)
    product2 = product_factory.create(price=15)
    order.add_product(product1, 2)
    order.add_product(product2, 3)
    assert order.total == 2 * 10 + 3 * 15


def test_count_orders_by_status(order_factory):
    """ Test orders count by status """
    expected = []
    for e in OrderStatusEnum:
        n = random.randint(1, 20)
        order_factory.create_batch(n, status=e)
        expected.append((e, n))
    expected.sort(key=lambda t: t[0].value)
    result = OrdersManager.count_by_status()
    result.sort(key=lambda t: t[0].value)
    assert expected == result


def test_product_sells(order_factory, product_factory):
    """ Test sells count for individual products """
    products = product_factory.create_batch(10)
    expected = []
    # For each product create n orders with other products in the detail and
    # add the product with a random quantity
    for p in products:
        total = 0
        orders = order_factory.create_batch(random.randint(1, 5), details=3)
        for o in orders:
            n = random.randint(1, 10)
            o.add_product(p, n)
            total += n
        expected.append((p, total))
    for e in expected:
        assert e[0].sells == e[1]


def test_products_sells_query(order_factory, product_factory):
    """ Test sells count for all products """
    products = product_factory.create_batch(10)
    expected = []
    # For each product create n orders with other products in the detail and
    # add the product with a random quantity
    for p in products:
        total = 0
        orders = order_factory.create_batch(random.randint(1, 5), details=3)
        for o in orders:
            for d in o.detail:
                expected.append((d.product, d.quantity))
            n = random.randint(1, 10)
            o.add_product(p, n)
            total += n
        expected.append((p, total))
    expected.sort(key=lambda v: v[0].id)
    result = ProductsManager.sells_by_product()
    result.sort(key=lambda v: v[0].id)
    assert expected == result


def test_units_delivered_by_product_by_country(
        order_factory, product_factory, country_factory, customer_factory):
    """ Count how many units of each product where delivered grouping by
        country """
    countries = country_factory.create_batch(5)
    customers = []
    for country in countries:
        customers += customer_factory.create_batch(5, country=country)
    products = product_factory.create_batch(20)
    expected = {}
    # Create random orders
    for _ in range(100):
        customer = random.choice(customers)
        product = random.choice(products)
        n = random.randint(1, 10)
        status = random.choice(list(OrderStatusEnum))
        order = order_factory.create(customer=customer, status=status)
        order.add_product(product, n)
        if status == OrderStatusEnum.DELIVERED:
            key = str(product.id)+'-'+str(customer.country.id)
            if key in expected:
                expected[key] += n
            else:
                expected[key] = n
    tmp = ProductsManager.units_delivered_by_product_by_country()
    result = {}
    for row in tmp:
        result[str(row[0].id)+'-'+str(row[1].id)] = row[2]
    assert result == expected
