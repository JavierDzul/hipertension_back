# app/schemas/risk_schema.py

REQUIRED_RISK_FIELDS = [
    "sex",
    "has_diabetes",
    "is_smoker",
    "systolic_bp",
    "age",
    "total_cholesterol",
]


def validate_risk_payload(data: dict) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    for field in REQUIRED_RISK_FIELDS:
        if field not in data:
            raise ValueError(f"El campo '{field}' es obligatorio.")

    sex = data.get("sex")

    if sex not in ["male", "female"]:
        raise ValueError("El sexo debe ser 'male' para hombre o 'female' para mujer.")

    has_diabetes = data.get("has_diabetes")
    is_smoker = data.get("is_smoker")

    if not isinstance(has_diabetes, bool):
        raise ValueError("El campo 'has_diabetes' debe ser verdadero o falso.")

    if not isinstance(is_smoker, bool):
        raise ValueError("El campo 'is_smoker' debe ser verdadero o falso.")

    try:
        systolic_bp = int(data.get("systolic_bp"))
        age = int(data.get("age"))
        total_cholesterol = int(data.get("total_cholesterol"))
    except (TypeError, ValueError):
        raise ValueError("La edad, presión sistólica y colesterol deben ser números enteros.")

    if age <= 0:
        raise ValueError("La edad debe ser mayor a 0.")

    if systolic_bp <= 0:
        raise ValueError("La presión arterial sistólica debe ser mayor a 0.")

    if total_cholesterol <= 0:
        raise ValueError("El colesterol total debe ser mayor a 0.")

    return {
        "sex": sex,
        "has_diabetes": has_diabetes,
        "is_smoker": is_smoker,
        "systolic_bp": systolic_bp,
        "age": age,
        "total_cholesterol": total_cholesterol,
    }