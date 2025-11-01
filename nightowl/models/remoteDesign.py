from nightowl.app import db
from sqlalchemy import ForeignKey

class RemoteDesign(db.Model):
  __tablename__ = "remote_design"
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100))
  ext_topic = db.Column(db.String(100)) 
  description = db.Column(db.String(100))
  data = db.Column(db.String(1000)) 

  def __init__(self,name,description, data, ext_topic):
    self.name = name
    self.description = description
    self.data = data
    self.ext_topic = ext_topic


