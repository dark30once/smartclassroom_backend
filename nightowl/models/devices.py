from nightowl.app import db
from sqlalchemy import ForeignKey

from nightowl.models.remoteDesign import RemoteDesign

class Devices(db.Model):
  __tablename__ = "devices"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100), unique = True)
  description = db.Column(db.String(100))
  remote_design_id = db.Column(db.Integer, ForeignKey('remote_design.id'))
  remote_design = db.relationship("RemoteDesign", backref = "devices")

  def __init__(self, name, description):
    self.name = name
    self.description = description
