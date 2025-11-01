from nightowl.app import db
from nightowl.models.groupAccess import GroupAccess

class Room(db.Model):
	__tablename__ = "room"
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100), unique = True)
	description = db.Column(db.String(100))

	def __init__(self, name, description):
		self.name = name
		self.description = description

	def __repr__(self):
		return 'Room( name = {self.name!r}, description = {self.description})'.format(self=self)





