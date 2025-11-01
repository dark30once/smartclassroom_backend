from nightowl.app import db
from sqlalchemy.orm import relationship

class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), unique = True)
    description = db.Column(db.String(100))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Permission):
            return NotImplemented
        return self.name == other.name

    def __repr__(self):
        return 'Permission(name = {self.name!r}, description = {self.description!r})'.format(self=self)
