from flask_restful import Resource, reqparse

from libs.auth import auth_required
from services.symbol_service import SymbolService
from controllers.symbol import api


class SymbolApi(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("symbols", type=str, required=True)
        args = parser.parse_args()
        result = SymbolService.query(args)
        return result, 200

api.add_resource(SymbolApi, '/symbol')
