import pytest
from flask import json, jsonify
from project import models

def test_get(client, category_factory):
    """ Retrieve one category """
    category1 = category_factory.create()
    category2 = category_factory.create()
    rv = client.get('/api/categories/%d' % category2.id)
    expected = {
        'id': category2.id,
        'name': category2.name
    }
    data = json.loads(rv.data)
    assert expected == data

def test_get_404(client, category_factory):
    """ Try to retrieve a non existing category """
    category = category_factory.create()
    rv = client.get('/api/categories/%d' % (category.id + 1))
    expected = {
        'status': 404,
        'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected == data

def test_list(client, category_factory):
    """ List all categories """
    categories = category_factory.create_batch(10)
    rv = client.get('/api/categories')
    expected = [{'id': category.id, 'name': category.name} for category in categories]
    data = json.loads(rv.data)
    expected.sort(key=lambda c: c['id'])
    data.sort(key=lambda c: c['id'])
    assert expected == data

def test_list_limit_offset(client, category_factory):
    """ List a range of categories """
    categories = category_factory.create_batch(10)
    rv = client.get('/api/categories?offset=1&limit=3')
    expected = [{'id': category.id, 'name': category.name} for category in categories[1:4]]
    data = json.loads(rv.data)
    expected.sort(key=lambda c: c['id'])
    data.sort(key=lambda c: c['id'])
    assert expected == data
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/categories?offset=4&limit=3'

def test_category_post(client, db_session):
    """ Create a new category """
    req = """ { "name": "category 1" } """
    rv = client.post('/api/categories', data=req, content_type='application/json')
    assert rv.status_code == 201
    assert int(rv.data) == 1
    category = models.Category.query.get(1)
    assert category is not None
    assert category.name == 'category 1'

def test_category_post_unique(client, category_factory):
    """ Try to create an already existing category """
    category = category_factory.create()
    req = """ { "name": "%s" } """ % category.name
    rv = client.post('/api/categories', data=req, content_type='application/json')
    assert rv.status_code == 400
    expected = {
       'status': 400,
       'message': 'Integrity error'
    }
    data = json.loads(rv.data)
    assert expected == data

def test_category_update(client, category_factory):
    """ Update a category """
    category = category_factory.create()
    new_name = category.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/categories/%d' % category.id, data=req, content_type='application/json')
    assert rv.status_code == 204
    assert category.name == new_name

def test_category_update_404(client, category_factory):
    """ Try to update a non existing category """
    category = category_factory.create()
    new_name = category.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/categories/2', data=req, content_type='application/json')
    assert rv.status_code == 404
    expected = {
       'status': 404,
       'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert expected == data

def test_category_delete(client, category_factory):
    """ Delete a category """
    category = category_factory.create()
    id = category.id
    rv = client.delete('/api/categories/%d' % category.id)
    assert rv.status_code == 204
    assert models.Category.query.get(id) is None

def test_category_delete_404(client, category_factory):
    """ Try to delete a non existing category """
    print(models.Category.query.count())
    category = category_factory.create()
    id = category.id
    rv = client.delete('/api/categories/2')
    assert rv.status_code == 404
    expected = {
       'status': 404,
       'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert expected == data
