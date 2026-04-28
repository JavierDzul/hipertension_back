# app/routes/alert_routes.py

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.alert_service import (
    get_user_alerts,
    resolve_alert,
    dismiss_alert,
    AlertError,
)
from app.utils.responses import success_response, error_response


alert_bp = Blueprint("alert_bp", __name__, url_prefix="/api/alerts")


@alert_bp.get("")
@jwt_required()
def get_alerts_route():
    user_id = int(get_jwt_identity())

    status = request.args.get("status", "active")
    limit = request.args.get("limit", 50)

    if status not in {"active", "resolved", "dismissed", "all"}:
        return error_response(
            message="El estado debe ser active, resolved, dismissed o all.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    try:
        limit = int(limit)
    except ValueError:
        return error_response(
            message="El límite debe ser un número entero.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    alerts = get_user_alerts(
        user_id=user_id,
        status=None if status == "all" else status,
        limit=limit,
    )

    return success_response(
        data=[alert.to_dict() for alert in alerts],
        message="Alertas obtenidas correctamente.",
    )


@alert_bp.patch("/<int:alert_id>/resolve")
@jwt_required()
def resolve_alert_route(alert_id: int):
    user_id = int(get_jwt_identity())

    try:
        alert = resolve_alert(user_id, alert_id)

        return success_response(
            data=alert.to_dict(),
            message="Alerta resuelta correctamente.",
        )

    except AlertError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@alert_bp.patch("/<int:alert_id>/dismiss")
@jwt_required()
def dismiss_alert_route(alert_id: int):
    user_id = int(get_jwt_identity())

    try:
        alert = dismiss_alert(user_id, alert_id)

        return success_response(
            data=alert.to_dict(),
            message="Alerta descartada correctamente.",
        )

    except AlertError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )