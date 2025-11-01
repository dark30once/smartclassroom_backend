from flask import Flask, redirect, url_for, request,render_template, flash, g
from ..exceptions import (UnauthorizedError, UnexpectedError, NotFoundError,
                          InvalidDataError)
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource
from datetime import datetime
from mqtt import mqtt
import json
import logging

from nightowl.models.roomStatus import RoomStatus
from nightowl.models.room import Room
from nightowl.models.devices import Devices
from nightowl.models.remoteDesign import RemoteDesign
from nightowl.models.usersLogs import UsersLogs

log = logging.getLogger(__name__)

class roomStatus(Resource): # for angular frontend app
    @requires("any", ["Admin", "User"])
    def get(self):
        rooms = sorted(g.current_user.getAccessibleRooms(["User", "Admin"]),
                       key=lambda x: x.name)
        all_data = {"room_status": []}

        totalDevice = Devices.query.count()

        for room in rooms:
            data = {"room_id": room.id,"room_name": room.name, "devices": []}
            statuses = sorted(room.room_status, key=lambda x: x.device.name)
            add_device = True
            if len(statuses) == totalDevice \
                    or "Admin" not in g.current_user.getRoomPermission(room):
                add_device = False
            data['add_device'] = add_device
            for queried_room_device in statuses:
                device = queried_room_device.device
                remote_design = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
                class_name = ""
                if remote_design.name == "Switch2":
                    class_name = "Door"
                device_details = {
                        "device_id": queried_room_device.device_id,
                        "device_name": device.name,
                        "device_status": queried_room_device.status,
                        "room_status_id": queried_room_device.id,
                        "remote_design": remote_design.name,
                        "remote_design_id": remote_design.id,
                        "class_name": class_name
                    }
                if remote_design.name == "Temperature Slider":
                    tem_details = json.loads(remote_design.data)
                    device_details.update(tem_details)
                data['devices'].append(device_details)
            all_data["room_status"].append(data)
        return all_data


class AllRoomStatus(Resource): # for mobile and other app
    @requires("any", ["Admin", "User"])
    def get(self):
        current_user = g.current_user
        rooms = sorted(current_user.getAccessibleRooms(["User", "Admin"]),
                       key=lambda x: x.name)

        all_data = {"room_status": []}
        totalDevice = Devices.query.count()

        for room in rooms:
            data = {"room_id": room.id,"room_name": room.name.upper(), "devices": []}
            statuses = sorted(room.room_status, key=lambda x: x.device.name)
            for rs in statuses:
                if rs.device.name == 'Door':
                    # Ignore Door Device
                    continue
                device = rs.device
                device_name = device.name
                device_status = rs.status
                if device.name == "Aircon temperature":
                    device_name = "Temp."
                if rs.status == "true":
                    device_status = "on"
                elif rs.status == "false":
                    device_status = "off"
                device_details = {
                        "device_name": device_name,
                        "device_status": device_status,
                    }
                data['devices'].append(device_details)
            all_data["room_status"].append(data)
        return all_data


class RoomStatusByRoomID(Resource):
    @requires("room", ["Admin", "User"])
    def get(self, id):
        current_user = g.current_user
        room = Room.query.get(id)
        if room is None:
            raise NotFoundError("room not found")
        data = {"room_id": room.id,"room_name": room.name, "date": datetime.strftime(datetime.today(),'%B %d %Y %A') , "devices": []}

        for rs in room.room_status:
            queried_device = rs.device
            device_details = {
                    "room_status_id": rs.id,
                    "device_name": queried_device.name,
                    "device_status": rs.status,
                }
            if queried_device.name == "Aircon temperature":
                if len(data['devices']) != 0:
                    data['devices'].insert(0,device_details)
                else:
                    data['devices'].append(device_details)
            else:
                data['devices'].append(device_details)
        return data


class RoomStatusByID(Resource): # for mobile and other app
    @requires("roomstatus", ["Admin"])
    def get(self, id):
        rs = RoomStatus.query.get(room_status_id)
        if rs is None:
            raise NotFoundError("room status not found")
        return {"id": rs.id, "status": rs.status}


class GetDeviceToAdd(Resource):
    @requires("room", ["Admin"])
    def get(self, id): # get all device not is not added to the room
        current_user = g.current_user
        room = Room.query.get(id)
        if room is None:
            raise NotFoundError("room not found")
        data = {"devices": []}

        room_devices = [rs.device for rs in room.room_status]
        devices = [d for d in Devices.query.all() if d not in room_devices]
        for device in devices:
            data['devices'].append({
                "id": device.id,
                "name": device.name,
                "description": device.description
            })
        return data


class AddDeviceToRoom(Resource):
    @requires("room", ["Admin"])
    def post(self, id):
        room = Room.query.get(id)
        if room is None:
            raise NotFoundError("room not found")
        data = request.get_json()

        for device_id in data:
            device = Devices.query.filter_by(id = device_id).first()
            remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
            if device == None:
                raise NotFoundError("device not found")
            if remoteDesign.name == "Temperature Slider":
                status = 24
            else:
                status = 'false'
            addDevice = RoomStatus(status = status, timestamp = datetime.today())
            addDevice.device = device
            addDevice.room = room
            db.session.add(addDevice)
            db.session.commit()
            room_status = RoomStatus.query.all()
            # print(">>>>==================================",room_status,len(room_status))
            # print("ADD-->")
        mqtt.publish("smartclassroom/reloadMqtt","true")

class AllRoomStatusByID(Resource):
    @requires("roomstatus", ["Admin", "User"])
    def put(self, id): #CONTROL DEVICES
        current_user = g.current_user
        room_status = RoomStatus.query.get(id)
        if room_status == None:
            raise NotFoundError("room status not found")

        payload = request.get_json()['value']
        log.debug("Received payload: {}".format(payload))
        if payload == True:
            payload = "true"
        elif payload == False:
            payload = "false"
        elif isinstance(payload, int) and payload>=16 and payload<=26:
            payload = int(payload)
        else:
            raise InvalidDataError("Invalid payload")
        data = get_room_status_details(room_status)
        log.debug("-----publish----")
        mqtt.publish("smartclassroom/"+str(data['room_name'])+"/"+str(data['device_name'])+"/"+str(data['ext_topic']),payload)

    @requires("roomstatus", ["Admin"])
    def delete(self, id):
        room_status = RoomStatus.query.get(id)
        if room_status == None:
            raise NotFoundError("room status not found")
        data = get_room_status_details(room_status)
        db.session.delete(room_status)
        db.session.commit()
        mqtt.publish("smartclassroom/reloadMqtt","true")
        log.debug("delete-->")

class Room_control_real_time_data(Resource):  # CHECK IF USER HAS REAL TIME IN ROOM CONTROL
    @requires("any", ["User", "Admin"])
    def get(self):
        current_user = g.current_user
        user = UsersLogs.query.filter_by(username = current_user.username)
        if user.count() == 0 or user.count() > 1:
            UnauthorizedError("user is not currently login")
        if user.first().room_control_real_time_data:
            return {"room_control_updated": True}
        if not user.first().room_control_real_time_data:
            user.one().room_control_real_time_data = True
            db.session.commit()
            return {"room_control_updated": False}


def get_room_status_details(room_status):

    room = Room.query.filter_by(id = room_status.room_id).first()
    device = Devices.query.filter_by(id = room_status.device_id).first()
    remoteDesign = RemoteDesign.query.filter_by(id = device.remote_design_id).first()

    return {"room_name": room.name, "device_name": device.name, "ext_topic": remoteDesign.ext_topic}


