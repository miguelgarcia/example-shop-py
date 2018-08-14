from flask import json
from project import models
from .utils import category_to_dict, expected_404, expected_integrity_error


def test_get(client, category_factory):
    """ Retrieve one category """
    category_factory.create()
    category2 = category_factory.create()
    rv = client.get('/api/categories/{:d}'.format(category2.id))
    data = json.loads(rv.data)
    expected = category_to_dict(category2)
    assert expected == data


def test_get_404(client, category_factory):
    """ Try to retrieve a non existing category """
    category = category_factory.create()
    rv = client.get('/api/categories/{:d}'.format(category.id + 1))
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected_404 == data


def test_list(client, category_factory):
    """ List all categories """
    categories = category_factory.create_batch(10)
    rv = client.get('/api/categories')
    expected = category_to_dict(categories)
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(
        data, key=lambda c: c['id'])


def test_list_limit_offset(client, category_factory):
    """ List a range of categories """
    categories = category_factory.create_batch(10)
    rv = client.get('/api/categories?offset=1&limit=3')
    expected = category_to_dict(categories[1:4])
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(
        data, key=lambda c: c['id'])
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/categories?offset=4\
&limit=3'


def test_category_post(client, db_session):
    """ Create a new category """
    req = {'name': 'category 1'}
    rv = client.post('/api/categories', data=json.dumps(req),
                     content_type='application/json')
    assert rv.status_code == 201
    created_id = int(rv.data)
    category = models.Category.query.get(created_id)
    assert category is not None
    assert category_to_dict(category, ['name']) == req


def test_category_post_unique(client, category_factory):
    """ Try to create an already existing category """
    category = category_factory.create()
    req = """ { "name": "%s" } """ % category.name
    rv = client.post('/api/categories', data=req,
                     content_type='application/json')
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert expected_integrity_error == data


def test_category_update(client, category_factory):
    """ Update a category """
    category = category_factory.create()
    new_name = category.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/categories/{:d}'.format(category.id),
                    data=req, content_type='application/json')
    assert rv.status_code == 204
    assert category.name == new_name


def test_category_update_404(client, category_factory):
    """ Try to update a non existing category """
    category = category_factory.create()
    new_name = category.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/categories/{:d}'.format(category.id+1),
                    data=req, content_type='application/json')
    assert rv.status_code == 404
    assert expected_404 == json.loads(rv.data)


def test_category_delete(client, category_factory):
    """ Delete a category """
    category = category_factory.create()
    id = category.id
    rv = client.delete('/api/categories/{:d}'.format(category.id))
    assert rv.status_code == 204
    assert models.Category.query.get(id) is None


def test_category_delete_404(client, category_factory):
    """ Try to delete a non existing category """
    category = category_factory.create()
    rv = client.delete('/api/categories/{:d}'.format(category.id + 1))
    assert rv.status_code == 404
    assert expected_404 == json.loads(rv.data)


def test_category_delete_used(client, product_factory, db_session):
    """ Delete a category """
    product = product_factory.create()
    product_id = product.id
    category_id = product.category.id
    rv = client.delete('/api/categories/{:d}'.format(category_id))
    assert rv.status_code == 400
    assert expected_integrity_error == json.loads(rv.data)
    db_session.expunge_all()
    product = models.Product.query.get(product_id)
    assert product.category.id == category_id
