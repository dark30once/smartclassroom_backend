from nightowl.models.devices import Devices
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class DevicesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Devices

devices_schema = DevicesSchema(only = ('id', 'name', 'description'))