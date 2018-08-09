from project.settings import ma
from marshmallow import validate
from project import models

class ListArgsSchema(ma.Schema):
    limit = ma.Integer(required=False, validate=[
                           validate.Range(1, 100)], missing=100)
    offset = ma.Integer(required=False, validate=[
                            validate.Range(0)], missing=0)

class CategorySchema(ma.ModelSchema):
    class Meta:
        model = models.Category
        fields = ('id', 'name')

class CountrySchema(ma.ModelSchema):
    class Meta:
        model = models.Country
        fields = ('id', 'name')
