from nightowl.app import db
from sqlalchemy import ForeignKey
from nightowl.models.groupMember import GroupMember
from nightowl.models.room import Room
import logging
from itertools import chain

log = logging.getLogger(__name__)

#------
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True)
    userpassword = db.Column(db.String(255))
    Fname = db.Column(db.String(100))
    Lname = db.Column(db.String(100))
    cardID = db.Column(db.String(100), unique=True)
    has_profile_picture = db.Column(db.Boolean)


    def __init__(self, username, userpassword, Fname,Lname, cardID, has_profile_picture):
        self.username = username
        self.userpassword = userpassword
        self.Fname = Fname
        self.Lname = Lname
        self.cardID = cardID
        self.has_profile_picture = has_profile_picture

    def _globalPermissions(self):
        perms = set()
        [perms.update(m.group.globalPermissions) for m in self.group_member]
        return perms

    def _allPermissions(self):
        perms = set()
        [perms.update(m.group.allPermissions) for m in self.group_member]
        return perms

    def _roomPermissions(self):
        perms = {}
        for m in self.group_member:
            for a in m.group.group_access:
                if a.room is not None:
                   perms.setdefault(a.permission.name, []).append(a.room)
        return perms

    def getAccessibleRooms(self, permissions):
        if set(permissions) & self.globalPermissions:
            log.debug("{} globally allowed".format(permissions))
            rooms = Room.query.all()
        else:
            room_perms =  dict([(k, v) for k,v in self.roomPermissions.items()
                                if k in permissions])
            log.debug("Room permissions: {}".format(room_perms))
            rooms = set(chain(*room_perms.values()))
        return rooms

    def getRoomPermission(self, room):
        perms = set()
        [perms.update(m.group.getRoomPermission(room))
         for m in self.group_member]
        return perms

    globalPermissions = property(_globalPermissions)
    allPermissions = property(_allPermissions)
    roomPermissions = property(_roomPermissions)

    def _userType(self):
        perms = self.allPermissions
        log.debug("Permissions for user {}: {}".format(self.id, perms))
        if "Admin" in perms:
            return "Admin"
        if "User" in perms:
            return "User"
        else:
            return "Guest"
    userType = property(_userType)

  # def __repr__(self):
  #       return 'Users(username = {self.username!r}, userpassword = {self.userpassword!r}, Fname = {self.Fname!r}, Lname = {self.Lname!r}, cardID = {self.cardID}, public_id = {self.public_id})'.format(self=self)

