from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.utils.serializers import serialize_user, serialize_profile

profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "user": serialize_user(user),
        "profile": serialize_profile(user.profile) if user.profile else None,
    }), 200


@profile_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json() or {}

    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)

    if not user.profile:
        user.profile = UserProfile(user_id=user.id)

    user.profile.birth_date = data.get("birth_date", user.profile.birth_date)
    user.profile.gender = data.get("gender", user.profile.gender)
    user.profile.weight_kg = data.get("weight_kg", user.profile.weight_kg)
    user.profile.height_m = data.get("height_m", user.profile.height_m)
    user.profile.blood_type = data.get("blood_type", user.profile.blood_type)
    user.profile.diagnosis = data.get("diagnosis", user.profile.diagnosis)
    user.profile.diagnosis_notes = data.get("diagnosis_notes", user.profile.diagnosis_notes)

    db.session.commit()

    return jsonify({
        "message": "Perfil actualizado correctamente",
        "user": serialize_user(user),
        "profile": serialize_profile(user.profile),
    }), 200