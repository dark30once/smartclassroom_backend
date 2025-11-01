from flask import make_response, request, jsonify
from ..exceptions import UnauthorizedError
from functools import wraps
from datetime import datetime
import jwt
from nightowl.app import db
import uuid

from ..models.users import Users
from ..models.usersLogs import UsersLogs
from ..models.group import Group
from ..models.groupMember import GroupMember
from ..models.permission import Permission
from ..app import app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = ''
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            url = str(request.url)

        if not token:
            return jsonify({'message' : 'token is missing'})

        # try:
        data = jwt.decode(token, app.config['SECRET_KEY'])
        print("=====",data)
        query = UsersLogs.query.filter_by(public_id = data['public_id'],username = data['username'])
        user = Users.query.filter_by(username =data['username'])
        if user.count() == 0 and query.count() == 0: # CHECK IF USER EXIST
            raise UnauthorizedError()
        elif user.count() == 1 and query.count() == 1:
            public_id = str(uuid.uuid4())
            userType = get_user_type(user.first().id)
            datetime_now = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
            token = jwt.encode({'username': user.first().username, 'public_id' : public_id, 'exp': datetime_now}, app.config['SECRET_KEY'])
            token = token.decode('UTF-8')
            if url.find("routeGuard") != -1 or url.find("shwNotGrpAccess") != -1 or url.find('groupDetails') != -1 or url.find('roomDetails') != -1:
                return f(userType, *args, **kwargs)
            user_details = {"userType": userType, "token": token, 'username': user.first().username}
            query.one().last_request_time = datetime_now
            query.one().public_id = public_id
            db.session.commit()
            return f(user_details, *args, **kwargs)
        else:
            raise UnauthorizedError()
        # except Exception as error:
        #     error = str(error)
        #     print("==>>",error)
        #     if error == "Signature has expired":
        #         raise InternalServerError({"message": "your token has been expired"})
        #     else:
        #         raise InternalServerError({"message": "Internal Server Error"})

    return decorated



def get_user_type(user_id):
    group_permission = []
    member = GroupMember.query.filter_by(user_id = user_id).all()
    if member == None:
        return "Guest"
    for queried_data in member:
        group = Group.query.filter_by(id = queried_data.group_id).first()
        permission = Permission.query.filter_by(id = group.permission_id).first()
        group_permission.append(permission.name)
    try:
        group_permission.index('Admin')
        return "Admin"
    except Exception as error:
        error = str(error)
        print(error)
    try:
        group_permission.index('User')
        return "User"
    except Exception as error:
        error = str(error)
        print(error)

    return "Guest"
