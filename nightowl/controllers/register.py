from flask_restx import Resource
from flask import request
import uuid
import bcrypt

from nightowl.models.users import Users
from nightowl.app import db

class register(Resource):
    def post(self):
        Request = request.get_json()
        if not Request['username'] or not Request['userpassword'] or not Request['Lname'] or not Request['Fname']:
                return {"message": "some parameters are missing"}
        cardid = Request.get('cardID', None)
        if len(Request['userpassword']) < 6:
            return {"message": "password must be more than 6 characters"}
        if Users.query.filter_by(username = Request['username']).count() == 0: #CHECK IF USER ALREADY EXIST
            pw = bcrypt.hashpw(Request['userpassword'].encode('UTF-8'), bcrypt.gensalt()).decode('utf-8')
            addUser = Users(username = Request['username'], userpassword = pw,
            Lname = Request['Lname'], Fname = Request['Fname'], cardID = cardid, has_profile_picture = False)
            db.session.add(addUser)
            db.session.commit()
            return {"response": "success"}
        else:
            return {'response': 'already exist'}
