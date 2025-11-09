from flask import Flask, redirect, url_for, request,render_template,flash, g
from ..exceptions import UnauthorizedError, UnexpectedError, InvalidDataError
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import requires
from flask_restful import Resource
import jwt

from nightowl.models.permission import Permission
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.users import Users
from nightowl.schema.permission import PermissionSchema
from nightowl.app import app
from sqlalchemy import and_


class permissions(Resource):
    @requires("global", ["Admin"])
    def get(self):
        allPermission = []
        permission_schema = PermissionSchema(many=True)
        queried_permissions = Permission.query.all()
        data = permission_schema.dump(queried_permissions)
        
        return {"permissions": data}

    @requires("global", ["Admin"])
    def post(self):
        permissions_schema = PermissionSchema()

        Request = request.get_json()
        addPermission = permissions_schema.load(Request, session = db.session).data
        name = addPermission.name
        if Permission.query.filter_by(name = name).count() == 0:
            db.session.add(addPermission)
            db.session.commit()
        else:
            raise InvalidDataError(
                "Permission {} already exist".format(name)
            )

class permission(Resource):
    @requires("global", ["Admin"])
    def delete(self, id):
        if GroupAccess.query.filter_by(permission_id = id).count() != 0:
            GroupAccess.query.filter_by(user_id = id).delete()
        Permission.query.filter_by(id = id).delete()
        db.session.commit()
        return {"response":'permission successfully deleted'}

    @requires("global", ["Admin"])
    def get(self, id):
        permission_schema = PermissionSchema(only = ('name', 'description'))
        query = Permission.query.filter_by(id = id)

        if query.count() != 0:
            permission = permission_schema.dump(query.first()).data
            return {"data": permission}
        else:
            return {"data": []}

    @requires("global", ["Admin"])
    def put(self, id):
        request_data = request.get_json()

        duplicate_perms = Permission.query.filter(
            and_(Permission.name == request_data['name'],
                 Permission.id != id))
        if duplicate_perms.count() > 0:
            raise InvalidDataError("permission already exist")
        else:
            query = Permission.query.get(id)
            query.name = request_data['name']
            query.description = request_data['description']
            db.session.commit()



class getAllPer(Resource):
    @requires("global", ["Admin"])
    def get(self):
        allPermission = []
        permission_schema = PermissionSchema(only = ('id', 'name', 'description'))
        permission = Permission.query.all()
        for queried_permission in permission:
            allPermission.append(permission_schema.dump(queried_permission).data)
        return {"permissions": allPermission}
