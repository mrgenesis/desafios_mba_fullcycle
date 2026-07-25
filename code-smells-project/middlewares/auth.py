from functools import wraps

from flask import request

from config import settings
from middlewares.errors import ApiError


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        chave = request.headers.get("X-Admin-Key")
        if chave != settings.ADMIN_KEY:
            raise ApiError({"erro": "Não autorizado", "sucesso": False}, 401)
        return f(*args, **kwargs)

    return wrapper
