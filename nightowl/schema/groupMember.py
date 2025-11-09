from nightowl.models.groupMember import GroupMember
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class GroupMemberSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = GroupMember


groupMember_schema = GroupMemberSchema()
