from flask_restful import Resource, reqparse
from controllers.term import api
from libs.auth import auth_required
from services.term_service import TermService

class TermApi(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("terms", type=str, required=True)
        args = parser.parse_args()
        result = TermService.query(args)
        return result, 200


api.add_resource(TermApi, '/term')
