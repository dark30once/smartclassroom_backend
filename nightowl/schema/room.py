from nightowl.models.room import Room
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class RoomSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Room
