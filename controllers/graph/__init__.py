from flask import Blueprint

from libs.external_api import ExternalApi

bp = Blueprint("graph", __name__, url_prefix="/api/v1")
api = ExternalApi(bp)

from . import index