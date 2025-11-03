from nightowl.models.auditTrail import AuditTrail
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class AuditTrailSchema(SQLAlchemyAutoSchema):
	class Meta:
		model = AuditTrail

auditTrial_schema = AuditTrailSchema()