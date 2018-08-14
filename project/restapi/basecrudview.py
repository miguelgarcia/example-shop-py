from flask.views import MethodView
from flask import jsonify, request
from .schemas import ListArgsSchema
from sqlalchemy.exc import IntegrityError
from project.app import db


class CrudView(MethodView):
    class Meta:
        model = None
        get_schema = None
        list_schema = None
        post_schema = None
        put_schema = None

    def __new__(cls, *args, **kwargs):
        o = super().__new__(cls)
        o._meta = getattr(o, 'Meta')
        return o

    def list(self):
        args_cleaned = ListArgsSchema().load(request.args)
        limit = args_cleaned.get('limit')
        offset = args_cleaned.get('offset')
        result = self.list_query(db.session, limit, offset)
        return (self._meta.list_schema(many=True).jsonify(result),
                200,
                {'x-next': "{:s}?offset={:d}&limit={:d}".format(
                    request.base_url,
                    offset+limit, limit)})

    def list_query(self, session, limit, offset):
        return self._meta.model.query.limit(limit).offset(offset)

    def get(self, id):
        if id is None:
            return self.list()
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify(dict(status=404, message='Not found')), 404
        return self._meta.get_schema().jsonify(o)

    def _try_commit(self):
        try:
            db.session.commit()
            return None
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'status': 400, 'message': 'Integrity error'}), 400
        except Exception:
            db.session.rollback()
            return jsonify({'status': 400, 'message': 'DB write error'}), 400

    def post(self):
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 400,
                            'message': 'No input data provided'}), 400
        o = self._meta.post_schema().load(json_data)
        db.session.add(o)
        resp = self._try_commit()
        return resp if resp is not None else (jsonify(o.id), 201)

    def delete(self, id):
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify({'status': 404, 'message': 'Not found'}), 404
        db.session.delete(o)
        resp = self._try_commit()
        return resp if resp is not None else ('', 204)

    def put(self, id):
        o = self._meta.model.query.get(id)
        if o is None:
            return jsonify({'status': 404, 'message': 'Not found'}), 404
        json_data = request.get_json()
        if not json_data:
            return jsonify({'status': 400,
                            'message': 'No input data provided'}), 400
        o = self._meta.put_schema().load(json_data, instance=o)
        resp = self._try_commit()
        return resp if resp is not None else ('', 204)
