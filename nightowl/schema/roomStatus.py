from nightowl.models.roomStatus import RoomStatus
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class RoomStatusSchema(SQLAlchemyAutoSchema):
  class Meta:
    model = RoomStatus

roomStatus_schema = RoomStatusSchema()