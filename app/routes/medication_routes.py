from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.medication import Medication
from app.utils.serializers import serialize_medication

medication_bp = Blueprint("medications", __name__)


@medication_bp.get("/medications")
@jwt_required()
def list_medications():
    user_id = int(get_jwt_identity())
    medications = (
        Medication.query.filter_by(user_id=user_id, is_active=True)
        .order_by(Medication.time.asc(), Medication.id.asc())
        .all()
    )

    return jsonify([serialize_medication(item) for item in medications]), 200


@medication_bp.post("/medications")
@jwt_required()
def create_medication():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    dose = (data.get("dose") or "").strip()
    time = (data.get("time") or "").strip()
    frequency = (data.get("frequency") or "").strip()
    notes = (data.get("notes") or "").strip()

    if not name or not dose or not time or not frequency:
        return jsonify({"error": "name, dose, time y frequency son obligatorios"}), 400

    medication = Medication(
        user_id=user_id,
        name=name,
        dose=dose,
        time=time,
        frequency=frequency,
        notes=notes or None,
    )

    db.session.add(medication)
    db.session.commit()

    return jsonify({
        "message": "Medicamento creado correctamente",
        "medication": serialize_medication(medication),
    }), 201


@medication_bp.patch("/medications/<int:medication_id>/take")
@jwt_required()
def mark_medication_taken(medication_id):
    user_id = int(get_jwt_identity())
    medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()

    if not medication:
        return jsonify({"error": "Medicamento no encontrado"}), 404

    medication.last_taken_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": "Medicamento marcado como tomado",
        "medication": serialize_medication(medication),
    }), 200


@medication_bp.delete("/medications/<int:medication_id>")
@jwt_required()
def delete_medication(medication_id):
    user_id = int(get_jwt_identity())
    medication = Medication.query.filter_by(id=medication_id, user_id=user_id).first()

    if not medication:
        return jsonify({"error": "Medicamento no encontrado"}), 404

    medication.is_active = False
    db.session.commit()

    return jsonify({"message": "Medicamento desactivado correctamente"}), 200