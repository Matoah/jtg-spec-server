import json

from enums.search_strategy import SearchStrategy
from libs.auth import auth_required
from flask_restful import Resource, reqparse
from controllers.segment import api
from retrieval.combined_retrieval import retrieve_document as combined_retrieve_document
from retrieval.graph_rag_retrieval import retrieve_document as graph_rag_retrieval
from  retrieval.hybrid_retrieval import retrieve_document as hybrid_retrieval

class SpecController(Resource):

    @auth_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, required=True)
        parser.add_argument("recommended_strategy", type=str, default=False, required=False)
        parser.add_argument("top_k", type=int, default=10, required=False)
        args = parser.parse_args()
        search_strategy = SearchStrategy(args.get("recommended_strategy"))
        if search_strategy == SearchStrategy.COMBINED:
            documents = combined_retrieve_document(args.get("query"), args.get("top_k"))
        elif search_strategy == SearchStrategy.GRAPH_RAG:
            documents = graph_rag_retrieval(args.get("query"), args.get("top_k"))
        else:
            documents = hybrid_retrieval(args.get("query"), args.get("top_k"))
        return json.dumps(documents), 200

api.add_resource(SpecController, "/segment")
