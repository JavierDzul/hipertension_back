from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.emergency_contact import EmergencyContact
from app.utils.serializers import serialize_contact

contact_bp = Blueprint("contacts", __name__)


@contact_bp.get("/contacts")
@jwt_required()
def list_contacts():
    user_id = int(get_jwt_identity())
    contacts = EmergencyContact.query.filter_by(user_id=user_id).order_by(EmergencyContact.id.asc()).all()
    return jsonify([serialize_contact(contact) for contact in contacts]), 200


@contact_bp.post("/contacts")
@jwt_required()
def create_contact():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    full_name = (data.get("full_name") or "").strip()
    relationship = (data.get("relationship") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not full_name or not relationship or not phone:
        return jsonify({"error": "full_name, relationship y phone son obligatorios"}), 400

    contact = EmergencyContact(
        user_id=user_id,
        full_name=full_name,
        relationship=relationship,
        phone=phone,
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify({
        "message": "Contacto creado correctamente",
        "contact": serialize_contact(contact),
    }), 201


@contact_bp.put("/contacts/<int:contact_id>")
@jwt_required()
def update_contact(contact_id):
    user_id = int(get_jwt_identity())
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=user_id).first()

    if not contact:
        return jsonify({"error": "Contacto no encontrado"}), 404

    data = request.get_json() or {}

    contact.full_name = data.get("full_name", contact.full_name)
    contact.relationship = data.get("relationship", contact.relationship)
    contact.phone = data.get("phone", contact.phone)

    db.session.commit()

    return jsonify({
        "message": "Contacto actualizado correctamente",
        "contact": serialize_contact(contact),
    }), 200


@contact_bp.delete("/contacts/<int:contact_id>")
@jwt_required()
def delete_contact(contact_id):
    user_id = int(get_jwt_identity())
    contact = EmergencyContact.query.filter_by(id=contact_id, user_id=user_id).first()

    if not contact:
        return jsonify({"error": "Contacto no encontrado"}), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({"message": "Contacto eliminado correctamente"}), 200