# app/schemas/auth_schema.py

import re


EMAIL_REGEX = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"


def validate_register_payload(data: dict) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not email:
        raise ValueError("El correo electrónico es obligatorio.")

    if not isinstance(email, str) or not re.match(EMAIL_REGEX, email):
        raise ValueError("El correo electrónico no tiene un formato válido.")

    if not full_name:
        raise ValueError("El nombre completo es obligatorio.")

    if not isinstance(full_name, str) or len(full_name.strip()) < 3:
        raise ValueError("El nombre completo debe tener al menos 3 caracteres.")

    if not password:
        raise ValueError("La contraseña es obligatoria.")

    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")

    return {
        "email": email.strip().lower(),
        "password": password,
        "full_name": full_name.strip(),
    }


def validate_login_payload(data: dict) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    email = data.get("email")
    password = data.get("password")

    if not email:
        raise ValueError("El correo electrónico es obligatorio.")

    if not password:
        raise ValueError("La contraseña es obligatoria.")

    return {
        "email": str(email).strip().lower(),
        "password": str(password),
    }