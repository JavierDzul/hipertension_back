# app/routes/risk_routes.py

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas.risk_schema import validate_risk_payload
from app.services.risk_service import (
    get_user_risk_profile,
    get_user_risk_history,
    upsert_user_risk_profile,
)
from app.system.globorisk_engine import GloboriskValidationError
from app.utils.responses import success_response, error_response


risk_bp = Blueprint("risk_bp", __name__, url_prefix="/api/risk-profile")


@risk_bp.get("")
@jwt_required()
def get_risk_profile():
    user_id = int(get_jwt_identity())

    profile = get_user_risk_profile(user_id)

    if profile is None:
        return success_response(
            data=None,
            message="Aún no se ha registrado un perfil de riesgo cardiovascular.",
        )

    return success_response(
        data=profile.to_dict(),
        message="Perfil de riesgo cardiovascular obtenido correctamente.",
    )


@risk_bp.put("")
@jwt_required()
def update_risk_profile():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        payload = validate_risk_payload(data)
        profile = upsert_user_risk_profile(user_id, payload)

        return success_response(
            data=profile.to_dict(),
            message="Perfil de riesgo cardiovascular actualizado correctamente.",
        )

    except ValueError as error:
        return error_response(
            message=str(error),
            code="VALIDATION_ERROR",
            status_code=400,
        )

    except GloboriskValidationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=400,
        )


@risk_bp.get("/history")
@jwt_required()
def get_risk_history():
    user_id = int(get_jwt_identity())

    limit = request.args.get("limit", 50)

    try:
        limit = int(limit)
    except ValueError:
        return error_response(
            message="El límite debe ser un número entero.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    history = get_user_risk_history(user_id=user_id, limit=limit)

    return success_response(
        data=[record.to_dict() for record in history],
        message="Historial de riesgo cardiovascular obtenido correctamente.",
    )