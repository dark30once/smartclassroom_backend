from nightowl.models.group import Group
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class GroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Group

    permission_id = fields.Int()
