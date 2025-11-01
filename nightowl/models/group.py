from nightowl.app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from nightowl.models.permission import Permission
from nightowl.models.groupAccess import GroupAccess
import logging

log = logging.getLogger(__name__)

class Group(db.Model):
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = True)
    description = db.Column(db.String(100))
    group_access = db.relationship("GroupAccess", backref = "group")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Group( name = {self.name!r}, description = {self.description})'.format(self=self)

    def _globalPermissions(self):
        return set([p.name for p in self.getGlobalPermissions()])

    def getGlobalPermissions(self):
        return [a.permission for a in self.group_access if a.room is None]

    def _permission(self):
        return self.getGlobalPermissions()[0]

    def _set_permission(self, permission):
        for a in self.group_access:
            if a.room is None:
                log.debug("Removing permission {}".format(a.permission.name))
                db.session.delete(a)
        ga = GroupAccess(permission=permission)
        db.session.add(ga)
        self.group_access.append(ga)
        log.debug("Adding permission {}".format(permission.name))
        db.session.commit()

    def _allPermissions(self):
        log.debug("Group Access for group {self.id}: {self.group_access}".\
                  format(self=self))
        return set([a.permission.name for a in self.group_access])

    def getRoomPermission(self, room):
        perms = set([a.permission.name for a in self.group_access
                     if a.room == room])
        perms.update(self.globalPermissions)
        return perms

    def _permission_id(self):
        return self.permission.id

    def _set_permission_id(self, permission_id):
        self.permission = Permission.query.get(permission_id)

    globalPermissions = property(_globalPermissions)
    allPermissions = property(_allPermissions)
    permission = property(_permission, _set_permission)
    permission_id = property(_permission_id, _set_permission_id)



    def _groupType(self):
        perms = self.allPermissions
        log.debug("Permissions for group {}: {}".format(self.id, perms))
        if "Admin" in perms:
            return "Admin"
        if "User" in perms:
            return "User"
        else:
            return "Guest"

    groupType = property(_groupType)



