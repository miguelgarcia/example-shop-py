import random

from flask import json
from project.models import (CustomersManager, OrdersManager, OrderStatusEnum,
                            ProductsManager)

from .utils import category_to_dict, country_to_dict, product_to_dict

# TODO:
# - Products sells
# - Units delivered by product by country


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
    assert sorted(expected, key=lambda c: c['category']['id']) == sorted(
        data, key=lambda c: c['category']['id'])


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
    assert sorted(expected, key=lambda c: c['country']['id']) == sorted(
        data, key=lambda c: c['country']['id'])


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
    assert sorted(expected, key=lambda c: c['status']) == sorted(
        data, key=lambda c: c['status'])


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
    assert sorted(expected, key=lambda c: c['product']['id']) == sorted(
        data, key=lambda c: c['product']['id'])
