from flask import Flask, redirect, url_for, request,render_template,flash, g
from ..exceptions import UnauthorizedError, UnexpectedError, InvalidDataError
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource

from nightowl.schema.room import RoomSchema
from nightowl.models.room import Room
from nightowl.models.groupAccess import GroupAccess
from nightowl.models.roomStatus import RoomStatus
from sqlalchemy import and_
import logging

log = logging.getLogger(__name__)

room_schema = RoomSchema(only = ( 'id', 'name', 'description' ))

class rooms(Resource):
    @requires("any", ["Admin", "User"])
    def get(self):
        rooms = g.current_user.getAccessibleRooms(["User", "Admin"])
        allRooms = []
        for room in rooms:
            data = room_schema.dump(room).data
            data['groups'] = len(room.group_access)
            allRooms.append(data)
        return {"rooms": allRooms}

    @requires("global", ["Admin"])
    def post(self):
        Request = request.get_json()
        addRoom = room_schema.load(Request, session = db.session).data
        name  = addRoom.name
        if Room.query.filter_by(name = name).count() == 0:
            db.session.add(addRoom)
            db.session.commit()
        else:
            raise InvalidDataError(
                "Room {} already exist".format(name)
            )

class room(Resource):
    @requires("room", ["Admin", "User"])
    def get(self, id):
        room = Room.query.get(id)
        data = room_schema.dump(room).data
        return {"data": data}


    @requires("room", ["Admin"])
    def delete(self, id):
        room = Room.query.get(id)
        if RoomStatus.query.filter_by(room_id = room.id).count() != 0:
            raise InvalidDataError("please remove devices before you delete room")
        GroupAccess.query.filter_by(room_id = room.id).delete()
        db.session.delete(room)
        db.session.commit()
        return {"response":'user successfully deleted'}

    @requires("room", ["Admin"])
    def put(self, id):
        request_data = request.get_json()
        room = Room.query.get(id)
        duplicate_rooms = Room.query.filter(
            and_(Room.name == request_data['name'],
                 Room.id != id))
        if duplicate_rooms.count() > 0:
            raise InvalidDataError("room already exist")
        room.name = request_data['name']
        room.description = request_data['description']
        db.session.commit()


class roomDetails(Resource): # THIS IS USER IN NAVBAT
    @requires("room", ["Admin", "User"])
    def get(self, id):
        room = Room.query.get(id)
        data = room_schema.dump(room).data
        return {"data":data}
