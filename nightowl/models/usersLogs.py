from nightowl.app import db
from sqlalchemy import ForeignKey
from nightowl.models.users import Users


class UsersLogs(db.Model):
  __tablename__ = "users_logs"
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(100))
  public_id = db.Column(db.String(300))
  time_login = db.Column(db.DateTime(timezone=True))
  last_request_time = db.Column(db.DateTime(timezone=True))
  status = db.Column(db.String(100))
  room_control_real_time_data = db.Column(db.Boolean(), nullable = True) # if true means user is updated and false is not


  def __init__(self, public_id, time_login, last_request_time, status, username, room_control_real_time_data):
    self.time_login = time_login
    self.public_id = public_id
    self.status = status
    self.last_request_time = last_request_time
    self.username = username
    self.room_control_real_time_data = room_control_real_time_data
