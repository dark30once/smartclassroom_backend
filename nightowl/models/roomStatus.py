from nightowl.app import db
from sqlalchemy import ForeignKey
from nightowl.models.room import Room
from nightowl.models.devices import Devices

class RoomStatus(db.Model):
  __tablename__ = "room_status"
  id = db.Column(db.Integer, primary_key = True)
  room_id = db.Column(db.Integer, ForeignKey('room.id'))
  device_id = db.Column(db.Integer, ForeignKey('devices.id'))
  status = db.Column(db.String(100))
  timestamp = db.Column(db.DateTime(timezone=True))

  room = db.relationship("Room", backref = "room_status")
  device = db.relationship("Devices", backref = "room_status")

  def __init__(self,status,timestamp):
    self.status = status
    self.timestamp = timestamp


