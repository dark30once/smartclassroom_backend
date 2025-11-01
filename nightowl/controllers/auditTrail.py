from flask import Flask, redirect, url_for, request,render_template,flash, g
from ..exceptions import UnauthorizedError, UnexpectedError
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource
from datetime import datetime

from nightowl.models.users import Users
from nightowl.models.room import Room
from nightowl.models.permission import Permission
from nightowl.models.auditTrail import AuditTrail
import logging

log = logging.getLogger(__name__)

class auditTrail(Resource):
    @requires("any", ["Admin", "User"])
    def get(self):
        current_user = g.current_user
        trail = sorted([
            at for room in current_user.getAccessibleRooms(['User', 'Admin'])
            for at in room.audit_trail],
                       key=lambda x: x.timestamp)
        all_data = []
        for tr in trail:
            auditTrail = {}
            user = tr.user
            room = tr.room
            permission = tr.permission
            if user is not None:
                auditTrail['username'] = user.username
                auditTrail['Fname'] = user.Fname
            else:
                auditTrail['username'] = None
                auditTrail['Fname'] = None
            if room is not None:
                auditTrail['room'] = room.name
            else:
                auditTrail['room'] = None
            if permission is not None:
                auditTrail['permission'] = permission.name
            else:
                auditTrail['permission'] = None
            auditTrail['timestamp'] = datetime.strftime(tr.timestamp,'%Y-%m-%d %I:%M %p')
            auditTrail['cardID'] = tr.cardID
            auditTrail['action'] = tr.action
            auditTrail['id'] = tr.id
            all_data.append(auditTrail)
        return {"auditTrail": all_data}

class deleteAuditTrail(Resource):
    @requires("global", ['Admin'])
    def delete(self,id):
        AuditTrail.query.get(id).delete()
        db.session.commit()

class delAllAuditTrail(Resource):
    @requires("global", ["Admin"])
    def delete(self):
        AuditTrail.query.delete()
        db.session.commit()
