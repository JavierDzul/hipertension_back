# app/routes/auth_routes.py

from flask import Blueprint, request

from app.schemas.auth_schema import (
    validate_register_payload,
    validate_login_payload,
)
from app.services.auth_service import (
    register_user,
    login_user,
    AuthError,
)
from app.utils.responses import success_response, error_response


auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json()

    try:
        payload = validate_register_payload(data)
        result = register_user(payload)

        return success_response(
            data=result,
            message="Cuenta creada correctamente.",
            status_code=201,
        )

    except ValueError as error:
        return error_response(
            message=str(error),
            code="VALIDATION_ERROR",
            status_code=400,
        )

    except AuthError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )


@auth_bp.post("/login")
def login():
    data = request.get_json()

    try:
        payload = validate_login_payload(data)
        result = login_user(payload)

        return success_response(
            data=result,
            message="Inicio de sesión realizado correctamente.",
            status_code=200,
        )

    except ValueError as error:
        return error_response(
            message=str(error),
            code="VALIDATION_ERROR",
            status_code=400,
        )

    except AuthError as error:
        return error_response(
            message=error.message,
            code=error.code,
            status_code=error.status_code,
        )