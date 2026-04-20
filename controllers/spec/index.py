from libs.auth import auth_required
from flask_restful import Resource, reqparse
from asgiref.sync import async_to_sync
from services.spec_service import SpecService
from controllers.spec import api

class SpecController(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, required=True)
        args = parser.parse_args()
        # sync_query = async_to_sync(SpecService.query)
        # result = sync_query(args)
        # return list(result)
        return SpecService.query(args)

api.add_resource(SpecController, "/spec")
