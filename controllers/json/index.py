import json

from libs.auth import auth_required
from flask_restful import Resource, reqparse
from controllers.json import api
from utils.text_util import try_parse_json_object


class JsonController(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("data", type=str, required=True, location="form")
        args = parser.parse_args()
        data = args.get("data")
        data,json_data = try_parse_json_object(data)
        return json_data, 200

api.add_resource(JsonController, "/json")
