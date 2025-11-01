from nightowl.models.devices import Devices
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class DevicesSchema(SQLAlchemyAutoSchema):
    # This explicitly declares the field and tells Marshmallow how to get its value
    description = fields.String()
    remote_design_id = fields.Int()  # Define the field
    class Meta:
    	model = Devices
    	# Add 'remote_design_id' to the fields you want to display
    	fields = ("id", "name", "description", "remote_design_id")

devices_schema = DevicesSchema(only = ('id', 'name', 'description', 'remote_design_id'))
# devices_schema = DevicesSchema(fields)