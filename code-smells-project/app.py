import logging

from flask import Flask
from flask_cors import CORS

import database
from config.settings import Settings
from middlewares.error_handler import register_error_handlers
from middlewares.security_headers import register_security_headers
from views import pedido_routes, produto_routes, relatorio_routes, sistema_routes, usuario_routes


def create_app(settings=Settings):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app, origins=settings.CORS_ORIGINS)

    database.init_app(app)

    for module in (produto_routes, usuario_routes, pedido_routes, relatorio_routes, sistema_routes):
        app.register_blueprint(module.bp)

    register_error_handlers(app)
    register_security_headers(app)
    return app


app = create_app()

if __name__ == "__main__":
    logging.getLogger(__name__).info("Servidor rodando em http://%s:%s", Settings.HOST, Settings.PORT)
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
