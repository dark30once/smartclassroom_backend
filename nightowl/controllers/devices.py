from flask import Flask, redirect, url_for, request,render_template,flash, g
from ..exceptions import UnauthorizedError, UnexpectedError, InvalidDataError
from flask import Blueprint
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource

from nightowl.models.devices import Devices
from nightowl.models.roomStatus import RoomStatus
from nightowl.models.remoteDesign import RemoteDesign

from nightowl.schema.devices import devices_schema


class devices(Resource):
    @requires("any", ["User", "Admin"])
    def get(self):
        all_devices = []
        devices = Devices.query.all()
        for device in devices:
            data = devices_schema.dump(device).data
            remote_design = RemoteDesign.query.filter_by(id = device.remote_design_id).first()
            if remote_design == None:
                data['remote_design'] = None
            else:
                data['remote_design'] = remote_design.name
            all_devices.append(data)
        return {'devices': all_devices}

    @requires("global", ["Admin"])
    def post(self):
        Request = request.get_json()
        if Devices.query.filter_by(name = Request['name']).count() != 0:
            raise InvalidDataError("Device {} already exist".format(Request['name']))
        addDevice = Devices(name = Request['name'],description = Request['description'])
        addDevice.remote_design = RemoteDesign.query.filter_by(id = Request['remote_design_id']).first()
        db.session.add(addDevice)
        db.session.commit()


class device(Resource):
    @requires("global", ["Admin"])
    def delete(self, id):
        if RoomStatus.query.filter_by(device_id = id).count() != 0:
            return {"message": "please remove devices from room before you delete device"}
        Devices.query.filter_by(id = id).delete()
        db.session.commit()
        return {"response":'device successfully deleted'}


    @requires("any", ["User", "Admin"])
    def get(self, id):
        query = Devices.query.get(id)

        if query.count() != 0:
            device = devices_schema.dump(query.first()).data
            device['remote_design'] = RemoteDesign.query.filter_by(id = device['remote_design_id']).first().name
            return {"data": device}
        else:
            return {"data": []}

    @requires("global", ["Admin"])
    def put(self, id):
        request_data = request.get_json()
        print(request_data)

        query = Devices.query.filter_by(name = request_data['name'])
        if query.count() > 0 and int(id) != query.first().id:
            return{"message": "device already exist"}
        else:
            query = Devices.query.filter_by(id = id).one()
            query.name = request_data['name']
            query.description = request_data['description']
            query.remote_design_id = RemoteDesign.query.filter_by(id = request_data['remote_design_id']).first().id
            db.session.commit()
