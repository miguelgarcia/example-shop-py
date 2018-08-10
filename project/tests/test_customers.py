import pytest
from flask import json, jsonify
from project import models
from .utils import model_to_dict, expected_404, expected_integrity_error

def test_get(client, customer_factory):
    """ Retrieve one customer """
    customer1 = customer_factory.create()
    customer2 = customer_factory.create()
    rv = client.get('/api/customers/%d' % customer2.id)
    data = json.loads(rv.data)
    expected = model_to_dict(customer2, ['id', 'email', 'firstname', 'lastname', ('country', ['id', 'name'])])
    assert expected == data

def test_get_404(client, customer_factory):
    """ Try to retrieve a non existing customer """
    customer = customer_factory.create()
    rv = client.get('/api/customers/%d' % (customer.id + 1))
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected_404 == data

def test_list(client, customer_factory):
    """ List all customers """
    customers = customer_factory.create_batch(10)
    rv = client.get('/api/customers')
    expected = model_to_dict(customers, ['id', 'email', 'firstname', 'lastname', ('country', ['id', 'name'])])
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(data, key=lambda c: c['id'])

def test_list_limit_offset(client, customer_factory):
    """ List a range of customers """
    customers = customer_factory.create_batch(10)
    rv = client.get('/api/customers?offset=1&limit=3')
    expected = model_to_dict(customers[1:4], ['id', 'email', 'firstname', 'lastname', ('country', ['id', 'name'])])
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(data, key=lambda c: c['id'])
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/customers?offset=4&limit=3'

def test_customer_post(client, country_factory, db_session):
    """ Create a new customer """
    country = country_factory.create()
    req = { 
        'email': 'customer1@example.com',
        'firstname': 'customer 1',
        'lastname': 'lastname 1',
        'country': country.id
    }
    rv = client.post('/api/customers', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 201
    assert int(rv.data) == 1
    customer = models.Customer.query.get(1)
    assert customer is not None
    expect = {
        'id': 1,
        'email': 'customer1@example.com',
        'firstname': 'customer 1',
        'lastname': 'lastname 1',
        'country': model_to_dict(country, ['id', 'name'])
    }
    assert model_to_dict(customer, ['id', 'email', 'firstname', 'lastname', ('country', ['id', 'name'])]) == expect

def test_customer_post_unique(client, customer_factory):
    """ Try to create an already existing customer """
    customer = customer_factory.create()
    req = model_to_dict(customer, ['email', 'firstname', 'lastname'])
    req['country'] = customer.country.id
    rv = client.post('/api/customers', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert expected_integrity_error == data

def test_customer_update(client, customer_factory, country_factory):
    """ Update a customer """
    customer = customer_factory.create()
    new_country = country_factory.create()
    req = { 
        'email': 'customer2@example.com',
        'firstname': 'customer 2',
        'lastname': 'lastname 2',
        'country': new_country.id
    }
    rv = client.put('/api/customers/%d' % customer.id, data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 204
    expect = req
    expect['country'] = { 'id': new_country.id }
    assert model_to_dict(customer, ['email','firstname', 'lastname', ('country', ['id'])]) == expect

def test_customer_update_404(client, customer_factory):
    """ Try to update a non existing customer """
    customer = customer_factory.create()
    req = { 
        'email': 'customer2@example.com',
        'firstname': 'customer 2',
        'lastname': 'lastname 2',
        'country': customer.country.id
    }
    rv = client.put('/api/customers/2', data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 404
    data = json.loads(rv.data)
    assert expected_404 == data

def test_customer_delete(client, customer_factory):
    """ Delete a customer """
    customer = customer_factory.create()
    id = customer.id
    rv = client.delete('/api/customers/%d' % customer.id)
    assert rv.status_code == 204
    assert models.Customer.query.get(id) is None

def test_customer_delete_404(client, customer_factory):
    """ Try to delete a non existing customer """
    customer = customer_factory.create()
    id = customer.id
    rv = client.delete('/api/customers/2')
    assert rv.status_code == 404
    data = json.loads(rv.data)
    assert expected_404 == data
