import pytest
from flask import json, jsonify
from project import models

def test_get(client, country_factory):
    """ Retrieve one country """
    country1 = country_factory.create()
    country2 = country_factory.create()
    rv = client.get('/api/countries/%d' % country2.id)
    expected = {
        'id': country2.id,
        'name': country2.name
    }
    data = json.loads(rv.data)
    assert expected == data

def test_get_404(client, country_factory):
    """ Try to retrieve a non existing country """
    country = country_factory.create()
    rv = client.get('/api/countries/%d' % (country.id + 1))
    expected = {
        'status': 404,
        'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected == data

def test_list(client, country_factory):
    """ List all countries """
    countries = country_factory.create_batch(10)
    rv = client.get('/api/countries')
    expected = [{'id': country.id, 'name': country.name} for country in countries]
    data = json.loads(rv.data)
    expected.sort(key=lambda c: c['id'])
    data.sort(key=lambda c: c['id'])
    assert expected == data

def test_list_limit_offset(client, country_factory):
    """ List a range of countries """
    countries = country_factory.create_batch(10)
    rv = client.get('/api/countries?offset=1&limit=3')
    expected = [{'id': country.id, 'name': country.name} for country in countries[1:4]]
    data = json.loads(rv.data)
    expected.sort(key=lambda c: c['id'])
    data.sort(key=lambda c: c['id'])
    assert expected == data
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/countries?offset=4&limit=3'

def test_country_post(client, db_session):
    """ Create a new country """
    req = """ { "name": "country 1" } """
    rv = client.post('/api/countries', data=req, content_type='application/json')
    assert rv.status_code == 201
    assert int(rv.data) == 1
    country = models.Country.query.get(1)
    assert country is not None
    assert country.name == 'country 1'

def test_country_post_unique(client, country_factory):
    """ Try to create an already existing country """
    country = country_factory.create()
    req = """ { "name": "%s" } """ % country.name
    rv = client.post('/api/countries', data=req, content_type='application/json')
    assert rv.status_code == 400
    expected = {
       'status': 400,
       'message': 'Integrity error'
    }
    data = json.loads(rv.data)
    assert expected == data

def test_country_update(client, country_factory):
    """ Update a country """
    country = country_factory.create()
    new_name = country.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/countries/%d' % country.id, data=req, content_type='application/json')
    assert rv.status_code == 204
    assert country.name == new_name

def test_country_update_404(client, country_factory):
    """ Try to update a non existing country """
    country = country_factory.create()
    new_name = country.name + "X"
    req = """ { "name": "%s" } """ % new_name
    rv = client.put('/api/countries/2', data=req, content_type='application/json')
    assert rv.status_code == 404
    expected = {
       'status': 404,
       'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert expected == data

def test_country_delete(client, country_factory):
    """ Delete a country """
    country = country_factory.create()
    id = country.id
    rv = client.delete('/api/countries/%d' % country.id)
    assert rv.status_code == 204
    assert models.Country.query.get(id) is None

def test_country_delete_404(client, country_factory):
    """ Try to delete a non existing country """
    country = country_factory.create()
    id = country.id
    rv = client.delete('/api/countries/2')
    assert rv.status_code == 404
    expected = {
       'status': 404,
       'message': 'Not found'
    }
    data = json.loads(rv.data)
    assert expected == data
