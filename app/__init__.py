from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, jwt
from app.routes.health_routes import health_bp
from app.routes.evaluation_routes import evaluation_bp
from app.routes.catalog_routes import catalog_bp
from app.routes.auth_routes import auth_bp
from app.routes.profile_routes import profile_bp
from app.routes.medication_routes import medication_bp
from app.routes.contact_routes import contact_bp
from app.routes.notification_routes import notification_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:5173"])

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(catalog_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(profile_bp, url_prefix="/api")
    app.register_blueprint(medication_bp, url_prefix="/api")
    app.register_blueprint(contact_bp, url_prefix="/api")
    app.register_blueprint(notification_bp, url_prefix="/api")
    app.register_blueprint(evaluation_bp, url_prefix="/api")

    return app