import random

from flask import json

from .utils import category_to_dict, country_to_dict
from project.models import ProductsManager, CustomersManager

# TODO:
# - Orders count by status
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
