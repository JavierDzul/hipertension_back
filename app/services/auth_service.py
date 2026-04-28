# app/services/auth_service.py

from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user import User


class AuthError(Exception):
    def __init__(self, message: str, code: str = "AUTH_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def register_user(payload: dict) -> dict:
    existing_user = User.query.filter_by(email=payload["email"]).first()

    if existing_user:
        raise AuthError(
            message="Ya existe una cuenta registrada con este correo electrónico.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=409,
        )

    user = User(
        email=payload["email"],
        full_name=payload["full_name"],
    )
    user.set_password(payload["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise AuthError(
            message="Ya existe una cuenta registrada con este correo electrónico.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=409,
        )

    access_token = create_access_token(identity=str(user.id))

    return {
        "user": user.to_dict(),
        "access_token": access_token,
    }


def login_user(payload: dict) -> dict:
    user = User.query.filter_by(email=payload["email"]).first()

    if not user or not user.check_password(payload["password"]):
        raise AuthError(
            message="Correo electrónico o contraseña incorrectos.",
            code="INVALID_CREDENTIALS",
            status_code=401,
        )

    access_token = create_access_token(identity=str(user.id))

    return {
        "user": user.to_dict(),
        "access_token": access_token,
    }


def get_user_by_id(user_id: int) -> User | None:
    return User.query.get(user_id)