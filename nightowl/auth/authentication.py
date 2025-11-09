from flask import make_response, request, jsonify, g
from werkzeug.exceptions import Unauthorized, InternalServerError
from functools import wraps
from datetime import datetime, timedelta
import jwt
from nightowl.app import db
import uuid
import logging

log = logging.getLogger(__name__)

from ..models.users import Users
from ..models.usersLogs import UsersLogs
from ..models.group import Group
from ..models.groupMember import GroupMember
from ..models.permission import Permission
from ..app import app
from ..models.room import Room
from ..models.roomStatus import RoomStatus
from ..exceptions import UnauthorizedError, UnexpectedError, NotFoundError
import json
import logging

log = logging.getLogger(__name__)

def login_user(request):
    token = ''
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        url = str(request.url)

    log.debug("Token: {}".format(token))
    if not token:
        raise UnauthorizedError('token is missing')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        log.debug("Token data: {}".format(data))
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("your token has been expired")
    except Exception:
        raise UnexpectedError("Error decoding token {}".format(token))

    user_log = UsersLogs.query.filter_by(public_id = data['public_id'],
                                         username = data['username'])
    try:
        user = Users.query.filter_by(username =data['username']).one()
    except:
        raise UnauthorizedError("User does not exist")
    #user_log.one().last_request_time = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')
    db.session.commit()

    token = jwt.encode({'username': data['username'], 'public_id' : data['public_id'], 'exp': datetime.now() + timedelta(days = 1)}, app.config['SECRET_KEY'])
    
    return user, token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        log.debug("Args: {}, kwargs: {}".format(args, kwargs))
        user, token = login_user(request)
        g.current_user = user
        g.token = token
        code = 200
        ret = f(*args, **kwargs)
        if isinstance(ret, tuple):
            code = ret[1]
            ret = ret[0]
        response = make_response(json.dumps(ret), code)
        response.headers.extend({'x-access-token': token})
        log.debug("Response: {}".format(response))
        return response
    return decorated

class requires():

    def __init__(self, require_type, permissions):
        self.req_type = require_type
        self.permissions = permissions
        perms_dict = {"room": self.checkRoomPermission,
                      "roomstatus": self.checkRoomStatusPermission,
                      "any": self.checkAnyPermission,
                      "global": self.checkGlobalPermission}
        self.perm_func = perms_dict[self.req_type]

    def checkGlobalPermission(self, user, *args, **kwargs):
        if not set(self.permissions) & set(user.globalPermissions):
            raise UnauthorizedError()
        return True

    def checkAnyPermission(self, user, *args, **kwargs):
        if not set(self.permissions) & set(user.allPermissions):
            raise UnauthorizedError()
        return True

    def checkRoomPermission(self, user, *args, **kwargs):
        log.debug("Checking room permission for {}, {}, {}".format(
            user, args, kwargs))
        room = Room.query.get(kwargs['id'])
        if room is None:
            raise NotFoundError("Room {} not found".format(kwargs['id']))
        perms = user.getRoomPermission(room)
        log.debug("Got permissions {}".format(perms))
        if not set(self.permissions) & perms:
            raise UnauthorizedError()
        return True

    def checkRoomStatusPermission(self, user, *args, **kwargs):
        log.debug("Checking room status permission for {}, {}, {}".format(
            user, args, kwargs))
        roomstatus = RoomStatus.query.get(kwargs['id'])
        if roomstatus is None:
            raise NotFoundError("Room {} not found".format(kwargs['id']))
        room = roomstatus.room
        perms = user.getRoomPermission(room)
        log.debug("Got permissions {}".format(perms))
        if not set(self.permissions) & perms:
            raise UnauthorizedError()
        return True

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            log.debug("{url} requires {self.req_type} permmissions "
                      "{self.permissions}".format(url=request.url, self=self))
            user, token = login_user(request)
            g.current_user = user
            g.token = token
            access = self.perm_func(user, *args, **kwargs)
            if 'permission_check' in kwargs.keys() and kwargs['permission_check']:
                #We only wanted to know whether we had permission to access
                #this url, not actually do/return anything. 
                return access
            code = 200
            ret = f(*args, **kwargs)
            if isinstance(ret, tuple):
                code = ret[1]
                ret = ret[0]
            response = make_response(json.dumps(ret), code)
            response.headers.extend({'x-access-token': token})
            log.debug("Response: {}".format(response))
            return response
        return wrapped

