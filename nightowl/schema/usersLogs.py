from nightowl.models.usersLogs import UsersLogs
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class UsersLogsSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = UsersLogs

users_logs_schema = UsersLogsSchema(only=('id','username','time_login','last_request_time', 'status'))