from configs import spec_server_config
from spec_app import SpecApp


def init_app(app: SpecApp):
    # register blueprint routers

    from flask_cors import CORS  # type: ignore

    from controllers.spec import bp as spec_bp

    from controllers.document import bp as document_bp

    from controllers.graph import bp as graph_bp

    from controllers.json import bp as json_bp

    from controllers.segment import bp as segment_bp

    CORS(
        spec_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    CORS(
        document_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    CORS(
        graph_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    CORS(
        json_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    CORS(
        segment_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    app.register_blueprint(document_bp)

    app.register_blueprint(graph_bp)

    app.register_blueprint(json_bp)

    app.register_blueprint(segment_bp)

    app.register_blueprint(spec_bp)

