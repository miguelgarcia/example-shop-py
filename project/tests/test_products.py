import pytest
from flask import json, jsonify
from project import models
from .utils import model_to_dict, expected_404, expected_integrity_error
import collections

def product_to_dict(product):
    if isinstance(product, collections.Iterable):
        return [product_to_dict(p) for p in product]
    d = model_to_dict(product, ['id', 'name', 'description', 
        ('category', ['id', 'name']), 'tags'])
    d['status'] = product.status.value
    d['tags'] = list(product.tags)
    d['price'] = '{:.2f}'.format(product.price)
    return d

def test_get(client, product_factory):
    """ Retrieve one product """
    product1 = product_factory.create()
    product2 = product_factory.create()
    rv = client.get('/api/products/%d' % product2.id)
    data = json.loads(rv.data)
    assert product_to_dict(product2) == data

def test_get_404(client, product_factory):
    """ Try to retrieve a non existing product """
    product = product_factory.create()
    rv = client.get('/api/products/{:d}'.format(product.id + 1))
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected_404 == data

def test_list(client, product_factory):
    """ List all products """
    products = product_factory.create_batch(10)
    rv = client.get('/api/products')
    expected = product_to_dict(products)
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(data, key=lambda c: c['id'])

def test_list_limit_offset(client, product_factory):
    """ List a range of products """
    products = product_factory.create_batch(10)
    rv = client.get('/api/products?offset=1&limit=3')
    expected = product_to_dict(products[1:4])
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(data, key=lambda c: c['id'])
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/products?offset=4&limit=3'

def test_product_post(client, category_factory, product_factory, tag_factory):
    """ Create a new product """
    category = category_factory.create()
    t = tag_factory.create(name='tag0')
    req = {
        'name': 'product 1',
        'description': 'Product description bla bla',
        'price': '10.55',
        'status': 'ACTIVE',
        'category': category.id,
        'tags': ['tag0', 'tag1']
    }    
    rv = client.post('/api/products', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 201
    assert int(rv.data) == 1
    product = models.Product.query.get(1)
    assert product is not None
    expect = req
    expect['id'] = 1
    expect['category'] = model_to_dict(category, ['id', 'name'])
    assert product_to_dict(product) == expect

def test_product_post_unique(client, product_factory):
    """ Try to create an already existing product """
    product = product_factory.create()
    req = product_to_dict(product)
    del req['id']
    req['category'] = product.category.id
    rv = client.post('/api/products', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert expected_integrity_error == data

def test_product_update(client, product_factory, category_factory):
    """ Update a product """
    product = product_factory.create()
    new_category = category_factory.create()
    req = product_to_dict(product)
    del req['id']
    req['name'] = 'new name'
    req['tags'] = ['other tag']
    req['category'] = new_category.id
    rv = client.put('/api/products/%d' % product.id, data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 204
    expect = req
    expect['id'] = 1
    expect['category'] = model_to_dict(new_category, ['id', 'name'])
    assert product_to_dict(product) == expect

def test_product_update_404(client, product_factory):
    """ Try to update a non existing product """
    product = product_factory.create()
    req = product_to_dict(product)
    del req['id']
    req['category'] = product.category.id
    rv = client.put('/api/products/2', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 404
    data = json.loads(rv.data)
    assert expected_404 == data

def test_product_delete(client, product_factory):
    """ Delete a product """
    product = product_factory.create()
    id = product.id
    rv = client.delete('/api/products/%d' % product.id)
    assert rv.status_code == 204
    assert models.Product.query.get(id) is None

def test_product_delete_404(client, product_factory):
    """ Try to delete a non existing product """
    product = product_factory.create()
    id = product.id
    rv = client.delete('/api/products/2')
    assert rv.status_code == 404
    data = json.loads(rv.data)
    assert expected_404 == data
