# app/routes/medication_routes.py

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas.medication_schema import (
    validate_medication_payload,
    validate_dose_log_payload,
)
from app.services.medication_service import (
    get_user_medications,
    get_user_medication,
    create_medication,
    update_medication,
    delete_medication,
    create_dose_log,
    get_medication_dose_logs,
    get_due_medications,
    MedicationError,
)
from app.utils.responses import success_response, error_response


medication_bp = Blueprint("medication_bp", __name__, url_prefix="/api/medications")


@medication_bp.post("")
@jwt_required()
def create_medication_route():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        payload = validate_medication_payload(data)
        medication = create_medication(user_id, payload)

        return success_response(
            data=medication.to_dict(),
            message="Medicamento registrado correctamente.",
            status_code=201,
        )

    except ValueError as error:
        return error_response(str(error))


@medication_bp.get("")
@jwt_required()
def get_medications_route():
    user_id = int(get_jwt_identity())

    medications = get_user_medications(user_id)

    return success_response(
        data=[medication.to_dict() for medication in medications],
        message="Medicamentos obtenidos correctamente.",
    )


@medication_bp.get("/due")
@jwt_required()
def get_due_medications_route():
    user_id = int(get_jwt_identity())

    due_medications = get_due_medications(user_id)

    return success_response(
        data=due_medications,
        message="Estado de tomas obtenido correctamente.",
    )


@medication_bp.get("/<int:medication_id>")
@jwt_required()
def get_medication_route(medication_id: int):
    user_id = int(get_jwt_identity())

    try:
        medication = get_user_medication(user_id, medication_id)

        return success_response(
            data=medication.to_dict(),
            message="Medicamento obtenido correctamente.",
        )

    except MedicationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@medication_bp.put("/<int:medication_id>")
@jwt_required()
def update_medication_route(medication_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        payload = validate_medication_payload(data, partial=True)
        medication = update_medication(user_id, medication_id, payload)

        return success_response(
            data=medication.to_dict(),
            message="Medicamento actualizado correctamente.",
        )

    except ValueError as error:
        return error_response(str(error))

    except MedicationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@medication_bp.delete("/<int:medication_id>")
@jwt_required()
def delete_medication_route(medication_id: int):
    user_id = int(get_jwt_identity())

    try:
        delete_medication(user_id, medication_id)

        return success_response(
            data=None,
            message="Medicamento eliminado correctamente.",
        )

    except MedicationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@medication_bp.post("/<int:medication_id>/dose-logs")
@jwt_required()
def create_dose_log_route(medication_id: int):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        payload = validate_dose_log_payload(data)
        dose_log = create_dose_log(user_id, medication_id, payload)

        return success_response(
            data=dose_log.to_dict(),
            message="Registro de toma guardado correctamente.",
            status_code=201,
        )

    except ValueError as error:
        return error_response(str(error))

    except MedicationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@medication_bp.get("/<int:medication_id>/dose-logs")
@jwt_required()
def get_dose_logs_route(medication_id: int):
    user_id = int(get_jwt_identity())

    limit = request.args.get("limit", 50)

    try:
        limit = int(limit)
        dose_logs = get_medication_dose_logs(user_id, medication_id, limit)

        return success_response(
            data=[dose_log.to_dict() for dose_log in dose_logs],
            message="Historial de tomas obtenido correctamente.",
        )

    except ValueError:
        return error_response(
            message="El límite debe ser un número entero.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    except MedicationError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )