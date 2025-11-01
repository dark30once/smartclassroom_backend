from nightowl.models.groupAccess import GroupAccess
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class GroupAccessSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = GroupAccess

groupAccess_schema = GroupAccessSchema()