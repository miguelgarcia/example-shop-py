import random

from flask import json
from app.models import (CustomersManager, OrdersManager, OrderStatusEnum,
                            ProductsManager)

from .utils import category_to_dict, country_to_dict, product_to_dict


def test_products_count_by_category(client, category_factory, product_factory):
    """ Products count by category """
    categories = category_factory.create_batch(10)
    counts = [random.randint(0, 10) for _ in categories]
    for i in range(len(counts)):
        product_factory.create_batch(counts[i], category=categories[i])
    rv = client.get('/api/statistics/products_by_category')
    data = json.loads(rv.data)
    expected = [{'category': category_to_dict(r.category), 'count': r.count}
                for r in ProductsManager.count_by_category()]

    def sort_key(item):
        return item['category']['id']
    assert sorted(expected, key=sort_key) == sorted(data, key=sort_key)


def test_customers_count_by_country(client, customer_factory, country_factory):
    """ Customers count by country """
    countries = country_factory.create_batch(10)
    counts = [random.randint(0, 10) for _ in countries]
    for i in range(len(counts)):
        customer_factory.create_batch(counts[i], country=countries[i])
    rv = client.get('/api/statistics/customers_by_country')
    data = json.loads(rv.data)
    expected = [{'country': country_to_dict(r.country), 'count': r.count}
                for r in CustomersManager.count_by_country()]

    def sort_key(item):
        return item['country']['id']
    assert sorted(expected, key=sort_key) == sorted(data, key=sort_key)


def test_count_orders_by_status(client, order_factory):
    """ Test orders count by status api """
    expected = []
    for e in OrderStatusEnum:
        n = random.randint(1, 20)
        order_factory.create_batch(n, status=e, details=random.randint(1, 3))
    expected = [{'status': r.status.value, 'count': r.count}
                for r in OrdersManager.count_by_status()]
    rv = client.get('/api/statistics/orders_by_status')
    data = json.loads(rv.data)

    def sort_key(item):
        return item['status']
    assert sorted(expected, key=sort_key) == sorted(data, key=sort_key)


def test_products_sells(client, order_factory, product_factory):
    """ Test sells count for individual products api """
    products = product_factory.create_batch(10)
    for p in products:
        total = 0
        orders = order_factory.create_batch(random.randint(1, 5))
        for o in orders:
            n = random.randint(1, 10)
            o.add_product(p, n)
            total += n
    expected = [{'product': product_to_dict(r.product), 'sells': r.sells}
                for r in ProductsManager.sells_by_product()]
    rv = client.get('/api/statistics/sells_by_product')
    data = json.loads(rv.data)

    def sort_key(item):
        return item['product']['id']
    assert sorted(expected, key=sort_key) == sorted(data, key=sort_key)


def test_units_delivered_by_product_by_country_api(
        client, order_factory, product_factory, country_factory,
        customer_factory):
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
        status = random.choice(list(OrderStatusEnum))
        order = order_factory.create(customer=customer, status=status)
        order.add_product(product, random.randint(1, 10))
    expected = [
            {
                'product_name': r.product_name,
                'product_id': r.product_id,
                'country_name': r.country_name,
                'country_id': r.country_id,
                'units': r.units
            }
            for r in ProductsManager.units_delivered_by_product_by_country()]
    rv = client.get('/api/statistics/units_delivered_by_product_by_country')
    data = json.loads(rv.data)

    def sort_key(item):
        return '{product_id}.{country_id}'.format(**item)
    assert sorted(expected, key=sort_key) == sorted(data, key=sort_key)
