import collections
import decimal
import enum
import datetime


def model_to_dict(model, fields):
    """ build dict from model object, only include fields listed in `fields`
      example: ['id', 'email', 'firstname', 'lastname',
        ('country', ['id', 'name'])
        ]
      will produce
      {
          id:
          email:
          firstname:
          lastname:
          country: {
              id:
              name:
          }
      }

      If model is a list returns a list of dicts, containing one dict for
      each model
     """
    if isinstance(model, collections.Iterable):
        return [model_to_dict(x, fields) for x in model]
    ret = dict()
    for f in fields:
        if isinstance(f, tuple):
            attr = f[0]
            ret[attr] = model_to_dict(getattr(model, attr), f[1])
        else:
            ret[f] = getattr(model, f)
            if isinstance(ret[f], decimal.Decimal):
                ret[f] = '{:.2f}'.format(ret[f])
            elif isinstance(ret[f], enum.Enum):
                ret[f] = ret[f].value
            elif isinstance(ret[f], datetime.datetime):
                ret[f] = ret[f].isoformat() + \
                    '+00:00' if ret[f].tzinfo is None else ''
    return ret


def category_to_dict(category, fields=None):
    if fields is None:
        fields = ['id', 'name']
    return model_to_dict(category, fields)


def country_to_dict(country, fields=None):
    if fields is None:
        fields = ['id', 'name']
    return model_to_dict(country, fields)


def product_to_dict(product):
    if isinstance(product, collections.Iterable):
        return [product_to_dict(p) for p in product]
    d = model_to_dict(product, ['id', 'name', 'description',
                                ('category', ['id', 'name']), 'tags'])
    d['status'] = product.status.value
    d['tags'] = list(product.tags)
    d['price'] = '{:.2f}'.format(product.price)
    return d


expected_404 = {
    'status': 404,
    'message': 'Not found'
}

expected_integrity_error = {
    'status': 400,
    'message': 'Integrity error'
}
