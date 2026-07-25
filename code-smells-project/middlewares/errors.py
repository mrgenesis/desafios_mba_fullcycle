from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, payload, status_code):
        super().__init__(payload.get("erro", "erro"))
        self.payload = payload
        self.status_code = status_code


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify(err.payload), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({"erro": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Erro não tratado")
        return jsonify({"erro": str(err)}), 500
