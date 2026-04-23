from libs.auth import auth_required
from flask_restful import Resource, reqparse
from controllers.graph import api
from retrieval.graph_rag_retrieval import retrieve_document

class JsonController(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, required=True, location="form")
        parser.add_argument("top_k", type=int, default=10, location="form")
        parser.add_argument("debug", type=bool, required=False, location="form")
        args = parser.parse_args()
        query = args.get("query")
        debug = args.get("debug")
        documents = retrieve_document(query, args.get("top_k"), debug)
        return "\n".join([doc.page_content for doc in documents]), 200, {"Content-Type": "text/plain"}

api.add_resource(JsonController, "/graph")
