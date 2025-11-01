from nightowl.app import db
from sqlalchemy import ForeignKey
from nightowl.models.users import Users
from nightowl.models.room import Room
from nightowl.models.permission import Permission

class AuditTrail(db.Model):
	__tablename__ = "audit_trail"
	id = db.Column(db.Integer, primary_key = True)
	timestamp = db.Column(db.DateTime(timezone=True))
	cardID = db.Column(db.String(100))
	action = db.Column(db.String(100))
	user_id = db.Column(db.Integer, ForeignKey('users.id'))
	room_id = db.Column(db.Integer, ForeignKey('room.id'))
	permission_id = db.Column(db.Integer, ForeignKey('permission.id'))

	user = db.relationship("Users", backref = "audit_trail")
	room = db.relationship("Room", backref = "audit_trail")
	permission = db.relationship("Permission", backref = "audit_trail")

	def __init__(self, timestamp,action,cardID):
		self.timestamp = timestamp
		self.action = action
		self.cardID = cardID




