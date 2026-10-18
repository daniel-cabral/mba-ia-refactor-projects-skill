import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from middlewares.security_headers import register_security_headers
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from routes.system_routes import system_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp


def create_app(config_object=Settings):
    logging.basicConfig(
        level=config_object.LOG_LEVEL,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )

    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app, origins=app.config['CORS_ORIGINS'])
    db.init_app(app)

    for blueprint in (system_bp, task_bp, user_bp, category_bp, report_bp):
        app.register_blueprint(blueprint)

    register_error_handlers(app)
    register_security_headers(app)

    with app.app_context():
        import models  # noqa: F401  (registers the models on the metadata)
        db.create_all()

    return app


if __name__ == '__main__':
    create_app().run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
