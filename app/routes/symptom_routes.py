# app/routes/symptom_routes.py

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.services.vital_service import get_available_symptoms
from app.utils.responses import success_response


symptom_bp = Blueprint("symptom_bp", __name__, url_prefix="/api/symptoms")


@symptom_bp.get("")
@jwt_required()
def get_symptoms_route():
    return success_response(
        data=get_available_symptoms(),
        message="Síntomas disponibles obtenidos correctamente.",
    )