from flask.views import MethodView
from flask import jsonify, request
from .schemas import ListArgsSchema
from sqlalchemy.exc import IntegrityError


class CrudView(MethodView):
    class Meta:
        model = None
        get_schema = None
        list_schema = None
        post_schema = None
        put_schema = None
        db = None

    def __new__(cls, *args, **kwargs):
        o = super(CrudView, cls).__new__(cls, *args, **kwargs)
        o._meta = getattr(o, 'Meta')
        return o

    def list(self):
        args_cleaned = ListArgsSchema().load(request.args)
        limit = args_cleaned.get('limit')
        offset = args_cleaned.get('offset')
        result = self._meta.model.query.limit(limit).offset(offset)
        return self._meta.list_schema(many=True).jsonify(result), 200, {'x-next': request.base_url + "?offset=%d&limit=%d" % (offset+limit, limit)}

    def get(self, id):
        if id is None:
            return self.list()
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify(dict(status=404, message='Not found')), 404
        return self._meta.get_schema().jsonify(o)

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 400, 'message': 'No input data provided'}), 400
        o = self._meta.post_schema().load(json_data)
        self._meta.db.session.add(o)
        try:
            self._meta.db.session.commit()
        except IntegrityError:
            return jsonify({'status': 400, 'message': 'Integrity error'}), 400
        return jsonify(o.id), 201

    def delete(self, id):
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify({'status': 404, 'message': 'Not found'}), 404
        self._meta.db.session.delete(o)
        self._meta.db.session.commit()
        return '', 204

    def put(self, id):
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify({'status': 404, 'message': 'Not found'}), 404
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 400, 'message': 'No input data provided'}), 400
        o = self._meta.put_schema().load(json_data, instance=o)
        try:
            self._meta.db.session.commit()
        except IntegrityError:
            return jsonify({'status': 400, 'message': 'Integrity error'}), 400
        return '', 204
