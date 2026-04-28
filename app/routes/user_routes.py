# app/routes/user_routes.py

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import get_user_by_id
from app.utils.responses import success_response, error_response


user_bp = Blueprint("user_bp", __name__, url_prefix="/api/users")


@user_bp.get("/me")
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())

    user = get_user_by_id(user_id)

    if not user:
        return error_response(
            message="Usuario no encontrado.",
            code="USER_NOT_FOUND",
            status_code=404,
        )

    return success_response(
        data=user.to_dict(),
        message="Usuario obtenido correctamente.",
    )