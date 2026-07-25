import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from config.database import init_db
from middlewares.errors import register_error_handlers
from routes import (
    admin_routes,
    health_routes,
    index_routes,
    pedido_routes,
    produto_routes,
    relatorio_routes,
    usuario_routes,
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    logging.basicConfig(level=logging.INFO)

    init_db(app)
    register_error_handlers(app)

    app.register_blueprint(index_routes.bp)
    app.register_blueprint(produto_routes.bp)
    app.register_blueprint(usuario_routes.bp)
    app.register_blueprint(pedido_routes.bp)
    app.register_blueprint(relatorio_routes.bp)
    app.register_blueprint(health_routes.bp)
    app.register_blueprint(admin_routes.bp)

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
