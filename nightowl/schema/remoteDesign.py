from nightowl.models.remoteDesign import RemoteDesign
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class RemoteDesignSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RemoteDesign
        

remote_design_schema = RemoteDesignSchema(only = ('id', 'name', 'description', 'data'))
