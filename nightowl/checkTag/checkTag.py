from flask_restx import Resource
from ..models.room import Room
from ..models.users import Users
from ..models.groupAccess import GroupAccess
from ..models.groupMember import GroupMember
from ..models.auditTrail import AuditTrail
from ..models.permission import Permission
from ..app import db
from datetime import datetime



class check_tag(Resource):
	def get(self, room_name, cardID):
		counter = False
		time_now = datetime.strptime(datetime.strftime(datetime.today(),'%Y-%m-%d %I:%M %p'),'%Y-%m-%d %I:%M %p')		
		room = Room.query.filter_by(name = room_name).first()
		user = Users.query.filter_by(cardID = cardID).first()		
		if room == None or user == None:
			auditTrail = AuditTrail(timestamp = time_now, action = "denied", cardID = cardID)
			auditTrail.user = user
			auditTrail.room = room			
			db.session.add(auditTrail)
			db.session.commit()
			return { "access": "denied"}		

		group_list = GroupMember.query.filter_by(user_id = user.id).all()		
		for member in group_list:			
			access = GroupAccess.query.filter_by(group_id = member.group_id, room_id = room.id).first()			
			if access != None:
				counter = True				
				auditTrail = AuditTrail(timestamp = time_now, action = "granted", cardID = cardID)
				auditTrail.user = user
				auditTrail.room = room				
				auditTrail.permission = Permission.query.filter_by(id = access.permission_id).first()
				db.session.add(auditTrail)
				db.session.commit()
				return { "access": "granted"}
		if counter == False:
			auditTrail = AuditTrail(timestamp = time_now, action = "denied", cardID = cardID)
			auditTrail.user = user
			auditTrail.room = room			
			db.session.add(auditTrail)
			db.session.commit()
			return { "access": "denied"}


		return {"message": "hello world"}