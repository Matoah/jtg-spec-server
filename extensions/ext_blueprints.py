from configs import spec_server_config
from spec_app import SpecApp


def init_app(app: SpecApp):
    # register blueprint routers

    from flask_cors import CORS  # type: ignore

    from controllers.spec import bp as spec_bp

    CORS(
        spec_bp,
        resources={r"/*": {"origins": spec_server_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    app.register_blueprint(spec_bp)

