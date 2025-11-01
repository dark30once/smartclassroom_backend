from nightowl.app import db
from sqlalchemy import ForeignKey

class GroupMember(db.Model):
	__tablename__ = "group_member"
	id = db.Column(db.Integer, primary_key = True)
	group_id = db.Column(db.Integer, ForeignKey('group.id'))
	user_id = db.Column(db.Integer, ForeignKey('users.id'))

	group = db.relationship("Group", backref = "group_member")
	user = db.relationship("Users", backref = "group_member")

