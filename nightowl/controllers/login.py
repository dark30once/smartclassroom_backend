from flask import request
from ..exceptions import UnauthorizedError, UnexpectedError
from nightowl.app import db
from flask_restful import Resource
import jwt
import bcrypt
from datetime import datetime, timedelta
import time
import uuid

from nightowl.app import db
from ..auth.authentication import token_required
from ..auth.authentication import app
from nightowl.models.users import Users
from nightowl.models.groupMember import GroupMember
from nightowl.models.group import Group
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.permission import Permission
import logging

log = logging.getLogger(__name__)



class login(Resource):
    def post(self):
        token = ''
        datetime_now = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
        public_id = str(uuid.uuid4())
        if 'x-access-token' in request.headers:
            log.debug("Already has an access token")
            token = request.headers['x-access-token']
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                user_log = UsersLogs.query.filter_by(username = data['username'], public_id = data['public_id'])
                try:
                   user = Users.query.filter_by(username = data['username']).one()
                except:
                    raise UnauthorizedError("Couldn't find user")
                if user_log.count() == 0:
                    return {"message": "user already logged out"}
                elif user_log.first().status != "active":
                    return {"message": "user already logged out"}
                token = jwt.encode({'username': data['username'], 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                
                userType = user.userType
                return {"token": token, 'userType': userType}
            except Exception as error:
                error = str(error)
                if error == "Signature has expired":
                    raise Unauthorized("your token has been expired")
                else:
                    raise UnexpectedError("Internal Server Error")

        Request = request.get_json()
        log.debug("Request data: {}".format(request.data))
        log.debug("Request json: {}".format(request.get_json()))
        log.debug("Request headers: {}".format(request.headers))
        if not Request['username']  and not Request['password']:
            raise UnexpectedError("username or password is not defined")
        else:
            try:
                user = Users.query.filter_by(username = Request['username']).one()
            except:
                raise UnauthorizedError("User does not exist")
            password = bcrypt.hashpw(Request['password'].encode('UTF-8'),
                                     user.userpassword.encode('UTF-8'))
            if user.userpassword.encode('UTF-8') == password: # CHECK IF PASSWORD IS CORRECT
                userType = user.userType
                already_login = UsersLogs.query.filter_by(username = user.username)
                if already_login.count() == 1:
                    update_active_user(public_id, datetime_now, already_login)
                    token = jwt.encode({'username': user.username, 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                    
                    return {'token': token, 'userType': userType}
                elif already_login.count() == 0:
                    add_active_user(user.username, public_id, datetime_now)
                    token = jwt.encode({'username': user.username, 'public_id' : public_id, 'exp': datetime_now + timedelta(days = 1)}, app.config['SECRET_KEY'])
                    
                    return {'token': token, 'userType': userType}
            else:
                raise UnauthorizedError("No user matching that name.")


class logout(Resource):
    def post(self):
        token = ''
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = UsersLogs.query.filter_by(username = data['username']).one().status = "logout"
            db.session.commit()
            return 200
        except Exception as error:
            error = str(error)
            print("==>>",error)
            if error == "Signature has expired":
                raise UnexpectedError({"message": "your token has been expired"})
            else:
                raise UnexpectedError({"message": "Internal Server Error"})


def add_active_user(username, public_id, time_login):
    add = UsersLogs(username = username, public_id = public_id, time_login = time_login , last_request_time = time_login, status = "active", room_control_real_time_data = True)
    db.session.add(add)
    db.session.commit()


def update_active_user(public_id, time_login, user):
    user.one().public_id = public_id
    user.one().time_login = time_login
    user.one().last_request_time = time_login
    user.one().status = "active"
    db.session.commit()


