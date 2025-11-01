from flask import request, send_file, jsonify, g
from ..exceptions import (UnauthorizedError, UnexpectedError, NotFoundError,
                          InvalidDataError)
from nightowl.app import db
from flask_restx import Resource
import uuid
import bcrypt
import jwt
import os
import logging

log = logging.getLogger(__name__)

from ..auth.authentication import token_required, requires

from nightowl.models.users import Users
from nightowl.models.groupMember import GroupMember
from nightowl.models.usersLogs import UsersLogs
from nightowl.models.group import Group
from nightowl.models.permission import Permission

from nightowl.app import app

from nightowl.schema.users import users_schema,addUsers_schema


class users(Resource):
    @requires('global', ['Admin'])
    def get(self):
        current_user = g.current_user
        allUser = []
        users = Users.query.filter(Users.username != current_user.username).all()
        for queried_user in users:
            allUser.append(users_schema.dump(queried_user).data)
        return { "users": allUser }

    @requires('global', ['Admin'])
    def post(self):
        Request = request.get_json()
        if not Request['username'] or not Request['userpassword'] or not Request['Lname'] or not Request['Fname']:
            return {"message": "some parameters is missing"}
        cardID = Request.get('cardID', '').strip() or None # make sure its not set if an empty string
        if len(Request['userpassword']) < 6:
            return {"message": "password must be more than 6 characters"}
        if Users.query.filter_by(username = Request['username']).count() == 0: #CHECK IF USER ALREADY EXIST
            pw = bcrypt.hashpw(Request['userpassword'].encode('UTF-8'), bcrypt.gensalt()).decode('utf-8')
            addUser = Users(username = Request['username'], userpassword = pw,
                            Lname = Request['Lname'], Fname = Request['Fname'], cardID = cardID, has_profile_picture = False)
            db.session.add(addUser)
            db.session.commit()
            return {"message": "success"}
        else:
            raise UnexpectedError('already exist')


class Get_account_photo(Resource):
    @token_required
    def put(self): #send user profile picture
        active_user = user = g.current_user
        if not user.has_profile_picture:
            return {"message": "user has no profile picture"}
        return send_file('image/user/'+str(user.id)+'.jpg', mimetype='image/jpg')


class editProfile(Resource):
    @token_required
    def get(self): # GET USER INFO USING TOKEN
        current_user = g.current_user
        return users_schema.dump(current_user)


class user(Resource):
    @requires("global", ["Admin"])
    def delete(self, id):
        if UsersLogs.query.filter_by(username = Users.query.filter_by(id = id).first().username).first():
            InvalidDataError("user is currently login")
        members = GroupMember.query.filter_by(user_id = id)
        users = Users.query.filter_by(id = id)
        if members.count() != 0:
            members.delete()
        if users.count() == 1:
            users.delete()
        db.session.commit()

    @requires("global", ["Admin"])
    def get(self, id): # GET USER INFO USING ID AND IT USE TO UPDATE USER
        query = Users.query.get(id)
        if query is None:
            raise NotFoundError("User {} was not found".format(id))
        user = users_schema.dump(query).data
        return {"data": user}

    @requires("global", ["Admin"])
    def put(self, id):
        values = request.values
        log.debug("request values: {}".format(values))
        query = Users.query.filter_by(username = values['username'])
        query2 = Users.query.filter_by(cardID = values['cardID'])

        if query.count() > 0 and query.first().id != int(id):
            raise InvalidDataError("username already exist")

        elif query2.count() > 0 and query2.first().id != int(id):
            raise InvalidDataError("cardID already exist")

        else:

            try:
                file = request.files['Image']
                if query.first().has_profile_picture:
                    os.remove("nightowl/image/user/"+str(id)+".jpg")
                image_file_name = str(id)+"."+'jpg'
                file.save(os.path.join('nightowl/image/user', image_file_name))
                photo = True
            except Exception as e:
                photo = False
                print(e,"error")
            cardID = values['cardID'] or None
            if cardID == 'null':
                cardID = None
            user = Users.query.filter_by(id = id).one()
            user.username = values['username']
            user.Fname = values['Fname']
            user.Lname = values['Lname']
            user.cardID = cardID
            if photo:
                user.has_profile_picture = True
            db.session.commit() 

class getUserProfile(Resource):    # THIS IS IN SIDEBAR HEADER

    @token_required
    def get(self):
        user = g.current_user
        member = GroupMember.query.filter_by(user_id = user.id).first()
        group = Group.query.filter_by(id = member.group_id).first()
        data = users_schema.dump(user).data
        if group.name[len(group.name)-1] == 's' or group.name[len(group.name)-1] == 'S':
            data['group_name'] = group.name[0:len(group.name)-1]
        else:
            data['group_name'] = group.name
        return data

class changePassword(Resource):
    @token_required
    def post(self):
        current_user = g.current_user
        print(current_user)
        data = request.get_json()
        user = Users.query.filter_by(username = current_user.username)
        if user == None:
            raise UnauthorizedError()
        if len(data['new_password']) < 6:
            return {"message": "password must be at least 6 characters"}
        password = bcrypt.hashpw(data['current_password'].encode('UTF-8'), user.first().userpassword.encode('UTF-8'))
        if user.first().userpassword.encode('UTF-8') != password:
            return {'message': 'invalid password'}
        new_password = bcrypt.hashpw(data['new_password'].encode('UTF-8'), bcrypt.gensalt()).decode('utf-8')
        user.one().userpassword = new_password
        db.session.commit()
        return {'message': 'your password is successfully changed'}
