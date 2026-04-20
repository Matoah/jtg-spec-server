from collections.abc import Callable
from functools import wraps

from flask import request, current_app
from configs import spec_server_config
from werkzeug.exceptions import Unauthorized
from flask_login.config import EXEMPT_METHODS

def auth_required(func: Callable):
    """
    认证装饰器, 对请求头中的Authorization字段进行验证
    :param func:
    :return:
    """
    @wraps(func)
    def decorator(*args, **kwargs):
        if spec_server_config.ADMIN_API_KEY_ENABLE:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                if " " not in auth_header:
                    raise Unauthorized(
                        "Invalid Authorization header format. Expected 'Bearer <api-key>' format."
                    )
                auth_scheme, auth_token = auth_header.split(None, 1)
                auth_scheme = auth_scheme.lower()
                if auth_scheme != "bearer":
                    raise Unauthorized(
                        "Invalid Authorization header format. Expected 'Bearer <api-key>' format."
                    )

                admin_api_key = spec_server_config.ADMIN_API_KEY
                if admin_api_key and auth_token != admin_api_key:
                    raise Unauthorized("Invalid Authorization")
            else:
                raise Unauthorized("Invalid Authorization header")
        if request.method in EXEMPT_METHODS or spec_server_config.LOGIN_DISABLED:
            pass

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorator
