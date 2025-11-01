from nightowl.app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from nightowl.models.permission import Permission

class GroupAccess(db.Model):
    __tablename__ = "group_access"
    id = db.Column(db.Integer, primary_key = True)
    room_id = db.Column(db.Integer, ForeignKey('room.id'))
    group_id = db.Column(db.Integer, ForeignKey('group.id'))
    permission_id = db.Column(db.Integer, ForeignKey('permission.id'))

    room = db.relationship("Room", backref = "group_access")
    permission = db.relationship("Permission", backref = "group_access")
