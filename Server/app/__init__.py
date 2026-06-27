from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS

from .errors import ApiError, error_response
from .config import config_by_name
from .extensions import db, jwt, migrate
from .routes.auth import auth_bp
from .routes.doors import doors_bp
from .routes.devices import devices_bp
from .routes.me import me_bp
from .routes.push_devices import push_devices_bp


def create_app(config_name=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )
    app.config.from_object(config_by_name(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_handlers(jwt)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(me_bp, url_prefix="/api")
    app.register_blueprint(doors_bp, url_prefix="/api/doors")
    app.register_blueprint(devices_bp, url_prefix="/api")
    app.register_blueprint(push_devices_bp, url_prefix="/api/push-devices")

    register_error_handlers(app)
    register_legacy_pages(app)
    register_cors(app)

    return app


def register_cors(app):
    if app.config["CORS_ENABLED"]:
        CORS(
            app,
            resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
            allow_headers=["Content-Type", "Authorization"],
            methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        )


def register_jwt_handlers(jwt_manager):
    @jwt_manager.unauthorized_loader
    def missing_token(message):
        return error_response("Authentication is required.", 401, "unauthorized")

    @jwt_manager.invalid_token_loader
    def invalid_token(message):
        return error_response("Invalid authentication token.", 401, "invalid_token")

    @jwt_manager.expired_token_loader
    def expired_token(header, payload):
        return error_response("Authentication token expired.", 401, "token_expired")


def register_legacy_pages(app):
    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.get("/sw.js")
    def serve_sw():
        return send_from_directory(app.static_folder, "sw.js")


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def api_error(error):
        return error_response(error.message, error.status_code, error.code)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": {"code": "bad_request", "message": "Bad request."}}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": {"code": "not_found", "message": "Not found."}}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify(
                {
                    "error": {
                        "code": "method_not_allowed",
                        "message": "Method not allowed.",
                    }
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return (
            jsonify(
                {
                    "error": {
                        "code": "internal_server_error",
                        "message": "Internal server error.",
                    }
                }
            ),
            500,
        )
