from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.extensions import db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.notification_preference import NotificationPreference
from app.utils.serializers import serialize_user, serialize_profile, serialize_notification_preferences

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/register")
def register():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()

    if not email or not password or not first_name or not last_name:
        return jsonify({"error": "email, password, first_name y last_name son obligatorios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Ese correo ya está registrado"}), 409

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        diagnosis="Hipertensión Grado 1",
        diagnosis_notes="Pendiente de completar por el usuario o médico.",
    )
    notifications = NotificationPreference(user_id=user.id)

    db.session.add(profile)
    db.session.add(notifications)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Usuario registrado correctamente",
        "access_token": access_token,
        "user": serialize_user(user),
    }), 201


@auth_bp.post("/auth/login")
def login():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "email y password son obligatorios"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Inicio de sesión correcto",
        "access_token": access_token,
        "user": serialize_user(user),
    }), 200


@auth_bp.get("/auth/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "user": serialize_user(user),
        "profile": serialize_profile(user.profile) if user.profile else None,
        "notifications": serialize_notification_preferences(user.notification_preferences)
        if user.notification_preferences
        else None,
    }), 200