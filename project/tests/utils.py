import collections

def model_to_dict(model, fields):
    """ build dict from model object, only include fields listed in `fields`
      example: ['id', 'email', 'firstname', 'lastname', ('country', ['id', 'name'])]
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

      If model is a list returns a list of dicts, containing one dict for each model
     """
    if isinstance(model, collections.Iterable):
        return [model_to_dict(x, fields) for x in model]
    ret = dict()
    for f in fields:
        if isinstance(f, tuple):
            attr = f[0]
            ret[attr] = model_to_dict(getattr(model,attr), f[1])
        else:
            ret[f] = getattr(model, f)
    return ret

expected_404 = {
    'status': 404,
    'message': 'Not found'
}    

expected_integrity_error = {
    'status': 400,
    'message': 'Integrity error'
}    