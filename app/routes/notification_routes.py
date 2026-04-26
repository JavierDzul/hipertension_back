from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.notification_preference import NotificationPreference
from app.utils.serializers import serialize_notification_preferences

notification_bp = Blueprint("notifications", __name__)


@notification_bp.get("/notifications/preferences")
@jwt_required()
def get_notification_preferences():
    user_id = int(get_jwt_identity())
    pref = NotificationPreference.query.filter_by(user_id=user_id).first()

    if not pref:
        pref = NotificationPreference(user_id=user_id)
        db.session.add(pref)
        db.session.commit()

    return jsonify(serialize_notification_preferences(pref)), 200


@notification_bp.put("/notifications/preferences")
@jwt_required()
def update_notification_preferences():
    user_id = int(get_jwt_identity())
    pref = NotificationPreference.query.filter_by(user_id=user_id).first()

    if not pref:
        pref = NotificationPreference(user_id=user_id)
        db.session.add(pref)

    data = request.get_json() or {}

    pref.critical_alerts = data.get("critical_alerts", pref.critical_alerts)
    pref.ai_trends = data.get("ai_trends", pref.ai_trends)
    pref.medication_reminders = data.get("medication_reminders", pref.medication_reminders)
    pref.missed_doses = data.get("missed_doses", pref.missed_doses)
    pref.daily_measurement = data.get("daily_measurement", pref.daily_measurement)
    pref.health_tips = data.get("health_tips", pref.health_tips)

    db.session.commit()

    return jsonify({
        "message": "Preferencias actualizadas correctamente",
        "preferences": serialize_notification_preferences(pref),
    }), 200