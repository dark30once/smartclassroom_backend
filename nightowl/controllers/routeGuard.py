from flask import request, g, current_app, make_response
from flask_restx import Resource
from ..auth.authentication import token_required
import urllib.parse as parser
import logging

log = logging.getLogger(__name__)


class routeGuard(Resource):
    @token_required
    def get(self):
        url = parser.unquote(request.args['url'])
        url_map = current_app.url_map.bind_to_environ(request.environ)
        endpoint, args = url_map.match(url)
        args['permission_check'] = True
        access = current_app.view_functions[endpoint](**args).get_json()
        return { "access": access}
