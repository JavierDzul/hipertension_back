# app/routes/vital_routes.py

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas.vital_schema import validate_vital_payload
from app.services.vital_service import (
    create_vital_record,
    get_user_vital_records,
    get_user_vital_record,
    get_available_symptoms,
    VitalRecordError,
)

from app.services.trend_service import get_vital_trends, TrendError
from app.utils.responses import success_response, error_response


vital_bp = Blueprint("vital_bp", __name__, url_prefix="/api/vitals")


@vital_bp.post("")
@jwt_required()
def create_vital_record_route():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        payload = validate_vital_payload(data)
        record = create_vital_record(user_id, payload)

        return success_response(
            data=record.to_dict(),
            message="Registro de signos vitales guardado correctamente.",
            status_code=201,
        )

    except ValueError as error:
        return error_response(
            message=str(error),
            code="VALIDATION_ERROR",
            status_code=400,
        )


@vital_bp.get("")
@jwt_required()
def get_vital_records_route():
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

    records = get_user_vital_records(user_id, limit)

    return success_response(
        data=[record.to_dict() for record in records],
        message="Historial de signos vitales obtenido correctamente.",
    )


@vital_bp.get("/symptoms")
@jwt_required()
def get_symptoms_route():
    return success_response(
        data=get_available_symptoms(),
        message="Síntomas disponibles obtenidos correctamente.",
    )


@vital_bp.get("/trends")
@jwt_required()
def get_vital_trends_route():
    user_id = int(get_jwt_identity())

    range_type = request.args.get("range", "week")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        trends = get_vital_trends(
            user_id=user_id,
            range_type=range_type,
            start_date=start_date,
            end_date=end_date,
        )

        return success_response(
            data=trends,
            message="Tendencias de signos vitales obtenidas correctamente.",
        )

    except TrendError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@vital_bp.get("/<int:record_id>")
@jwt_required()
def get_vital_record_route(record_id: int):
    user_id = int(get_jwt_identity())

    try:
        record = get_user_vital_record(user_id, record_id)

        return success_response(
            data=record.to_dict(),
            message="Registro de signos vitales obtenido correctamente.",
        )

    except VitalRecordError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )