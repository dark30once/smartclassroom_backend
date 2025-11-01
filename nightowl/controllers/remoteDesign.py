from flask import request, g
from ..exceptions import UnauthorizedError
from nightowl.app import db
from ..auth.authentication import requires
from flask_restx import Resource

from nightowl.schema.remoteDesign import remote_design_schema

from nightowl.models.remoteDesign import RemoteDesign


class AllRemoteDesign(Resource):
    @requires("global", ["Admin"])
    def get(self):
        all_data = {"remote_design": []}
        datas = RemoteDesign.query.all()
        for data in datas:
            all_data['remote_design'].append(remote_design_schema.dump(data).data)
        return all_data
