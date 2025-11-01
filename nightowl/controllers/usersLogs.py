from flask import request, g
from ..exceptions import UnauthorizedError
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource
from datetime import datetime

from nightowl.models.usersLogs import UsersLogs

from nightowl.schema.usersLogs import users_logs_schema


class activeUsers(Resource):
    @requires("global", ["Admin"])
    def get(self):
        active_user = []
        user = UsersLogs.query.all()
        for queried_user in user:
            data = users_logs_schema.dump(queried_user).data
            data['last_request_time'] = datetime.strftime(queried_user.last_request_time,'%Y-%m-%d %I:%M %p')
            data['time_login'] = datetime.strftime(queried_user.time_login,'%Y-%m-%d %I:%M %p')
            active_user.append(data)
        return {"users": active_user}

class delActiveUser(Resource):
    @requires("global", ["Admin"])
    def delete(self, id):
        UsersLogs.query.filter_by(id = id).delete()
        db.session.commit()

