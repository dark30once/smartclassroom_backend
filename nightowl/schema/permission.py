from nightowl.models.permission import Permission
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class PermissionSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Permission
