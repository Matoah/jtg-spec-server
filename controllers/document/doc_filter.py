import json
from pyexpat import features

from libs.auth import auth_required
from flask_restful import Resource, reqparse
from controllers.document import api
from models.document_filter import DocumentFilter
from utils.dict_util import is_all_empty
from retrieval.hybrid_retrieval import get_document_md5_list
from utils.text_util import try_parse_json_object

class JsonController(Resource):

    @auth_required
    def post(self):
        """
        根据特征信息，过滤文档，返回文档md5列表
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument("feature", type=str, required=True, location="form")
        args = parser.parse_args()
        feature = args.get("feature")
        json_text,feature_data = try_parse_json_object(feature)
        if is_all_empty(feature_data):
            return json.dumps([]), 200
        else:
            doc_filter = DocumentFilter(**feature_data)
            document_md5_list = get_document_md5_list(doc_filter)
            return json.dumps(document_md5_list, ensure_ascii=False), 200

api.add_resource(JsonController, "/doc_filter")
