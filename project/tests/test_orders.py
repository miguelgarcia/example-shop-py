import collections
import datetime
import random

import dateutil
from flask import json
from project import models

from .utils import expected_404, model_to_dict


def order_to_dict(order, fields=None):
    if fields is None:
        fields = ['id', 'created_at', 'total', 'status',
                  ('customer', ['id', 'email', 'firstname', 'lastname']),
                  ('detail', ['id', 'quantity', 'unit_price',
                              ('product', ['id', 'name'])]
                   )]
    if isinstance(order, collections.Iterable):
        return [order_to_dict(o, fields) for o in order]
    d = model_to_dict(order, fields)
    return d


def test_order_get(client, order_factory):
    """ Retrieve one order """
    order_factory.create(details=3)
    order2 = order_factory.create(details=3)
    rv = client.get('/api/orders/{:d}'.format(order2.id))
    data = json.loads(rv.data)
    assert order_to_dict(order2) == data


def test_get_404(client, order_factory):
    """ Try to retrieve a non existing order """
    order = order_factory.create()
    rv = client.get('/api/orders/{:d}'.format(order.id + 1))
    data = json.loads(rv.data)
    assert rv.status_code == 404
    assert expected_404 == data


def test_orders_list(client, order_factory):
    """ List all orders """
    orders = order_factory.create_batch(10, details=3)
    list_fields = ['id', 'created_at', 'total', 'status',
                   ('customer', ['id', 'email', 'firstname', 'lastname'])]
    expected = order_to_dict(orders, list_fields)
    rv = client.get('/api/orders')
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(
        data, key=lambda c: c['id'])


def test_list_limit_offset(client, order_factory):
    """ List a range of orders """
    orders = order_factory.create_batch(10)
    list_fields = ['id', 'created_at', 'total', 'status',
                   ('customer', ['id', 'email', 'firstname', 'lastname'])]
    expected = order_to_dict(orders[1:4], list_fields)
    rv = client.get('/api/orders?offset=1&limit=3')
    data = json.loads(rv.data)
    assert sorted(expected, key=lambda c: c['id']) == sorted(
        data, key=lambda c: c['id'])
    assert 'x-next' in rv.headers
    assert rv.headers['x-next'] == 'http://localhost/api/orders?offset=4\
&limit=3'


def test_order_post(client, customer_factory, product_factory):
    """ Create a new order """
    customer = customer_factory.create()
    products = product_factory.create_batch(3)
    quantities = [random.randint(1, 10) for p in products]
    req = {
        'customer': customer.id,
        'detail': [
            {
                'product': products[idx].id,
                'quantity': quantities[idx],
            }
            for idx in range(len(products))
        ]
    }
    rv = client.post('/api/orders', data=json.dumps(req),
                     content_type='application/json')
    assert rv.status_code == 201
    created_id = int(rv.data)
    order = models.Order.query.get(created_id)
    assert order is not None
    expect = {
        'id': created_id,
        'status': 'PENDING',
        'customer': model_to_dict(
            customer, ('id', 'email', 'firstname', 'lastname')),
        'detail': [
            {
                'id': order.detail[idx].id,
                'product': model_to_dict(products[idx], ('id', 'name')),
                'quantity': quantities[idx],
                'unit_price': '{:.2f}'.format(products[idx].price)
            }
            for idx in range(len(products))
        ],
        'total': '{:.2f}'.format(
            sum([products[idx].price * quantities[idx]
                for idx in range(len(products))]))
    }
    actual = order_to_dict(order)
    created_at = dateutil.parser.parse(actual['created_at'], ignoretz=True)
    assert created_at.timestamp() - datetime.datetime.now().timestamp() < 10
    del actual['created_at']
    assert actual == expect


def test_order_update(client, order_factory):
    """ Update a order """
    order = order_factory.create()
    req = {
        'status': models.OrderStatusEnum.SHIPPING.value
    }
    rv = client.put('/api/orders/{:d}'.format(order.id),
                    data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 204
    assert order.status == models.OrderStatusEnum.SHIPPING


def test_order_update_404(client, order_factory):
    """ Try to update a non existing order """
    order = order_factory.create()
    req = {
        'status': models.OrderStatusEnum.SHIPPING.value
    }
    rv = client.put('/api/orders/{:d}'.format(order.id+1),
                    data=json.dumps(req), content_type='application/json')
    assert rv.status_code == 404
    assert expected_404 == json.loads(rv.data)


def test_order_cant_delete(client, order_factory):
    """ Try to delete an order """
    order = order_factory.create()
    rv = client.delete('/api/orders/{:d}'.format(order.id))
    assert rv.status_code == 405
