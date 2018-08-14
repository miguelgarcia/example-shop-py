import random

from flask import json

from .utils import category_to_dict


def test_products_count_by_category(client, category_factory, product_factory):
    categories = category_factory.create_batch(10)
    counts = [random.randint(0, 10) for _ in categories]
    for i in range(len(counts)):
        product_factory.create_batch(counts[i], category=categories[i])
    rv = client.get('/api/statistics/products_by_category')
    expected = [{
        'category': category_to_dict(categories[i]),
        'count': counts[i]
    } for i in range(len(counts))]
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['category']['id']) == sorted(
        data, key=lambda c: c['category']['id'])
