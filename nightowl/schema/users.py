from nightowl.models.users import Users
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

class UsersSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = Users

users_schema = UsersSchema(only=('id','username','Fname','Lname','cardID'))
addUsers_schema = UsersSchema()