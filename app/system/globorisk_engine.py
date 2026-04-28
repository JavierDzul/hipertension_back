# app/system/globorisk_engine.py

from typing import Any

from app.system.globorisk_tables import GLOBORISK_TABLE


VALID_SEX_VALUES = {"male", "female"}


class GloboriskValidationError(Exception):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


def get_age_bucket(age: int) -> int | None:
    if age < 40:
        return None

    if age <= 44:
        return 40
    if age <= 49:
        return 45
    if age <= 54:
        return 50
    if age <= 59:
        return 55
    if age <= 64:
        return 60
    if age <= 69:
        return 65
    if age <= 74:
        return 70
    if age <= 79:
        return 75

    return 80


def get_systolic_bucket(systolic_bp: int) -> int:
    if systolic_bp < 120:
        raise GloboriskValidationError(
            "La presión arterial sistólica debe ser de al menos 120 mmHg para calcular GLOBORISK."
        )

    if systolic_bp <= 139:
        return 120
    if systolic_bp <= 159:
        return 140
    if systolic_bp <= 179:
        return 160

    return 180


def get_cholesterol_bucket(total_cholesterol: int) -> int:
    if total_cholesterol < 116:
        raise GloboriskValidationError(
            "El colesterol total debe ser de al menos 116 mg/dl para calcular GLOBORISK."
        )

    if total_cholesterol <= 153:
        return 116
    if total_cholesterol <= 192:
        return 154
    if total_cholesterol <= 231:
        return 193
    if total_cholesterol <= 269:
        return 232

    return 270


def get_risk_category_label(risk_percent: float, is_less_than_one: bool = False) -> str:
    if is_less_than_one:
        return "Riesgo muy bajo"

    if risk_percent < 1:
        return "Riesgo muy bajo"
    if risk_percent == 1:
        return "Riesgo bajo"
    if risk_percent == 2:
        return "Riesgo bajo"
    if 3 <= risk_percent <= 4:
        return "Riesgo moderado bajo"
    if 5 <= risk_percent <= 9:
        return "Riesgo moderado"
    if 10 <= risk_percent <= 14:
        return "Riesgo alto"

    return "Riesgo muy alto"


def validate_globorisk_input(
    sex: str,
    has_diabetes: bool,
    is_smoker: bool,
    systolic_bp: int,
    age: int,
    total_cholesterol: int,
) -> None:
    if sex not in VALID_SEX_VALUES:
        raise GloboriskValidationError(
            "El sexo debe ser 'male' para hombre o 'female' para mujer."
        )

    if not isinstance(has_diabetes, bool):
        raise GloboriskValidationError("El campo de diabetes debe ser verdadero o falso.")

    if not isinstance(is_smoker, bool):
        raise GloboriskValidationError("El campo de fumador debe ser verdadero o falso.")

    if age <= 0:
        raise GloboriskValidationError("La edad debe ser mayor a 0.")

    if systolic_bp <= 0:
        raise GloboriskValidationError("La presión arterial sistólica debe ser mayor a 0.")

    if total_cholesterol <= 0:
        raise GloboriskValidationError("El colesterol total debe ser mayor a 0.")


def calculate_globorisk(
    sex: str,
    has_diabetes: bool,
    is_smoker: bool,
    systolic_bp: int,
    age: int,
    total_cholesterol: int,
) -> dict[str, Any]:
    validate_globorisk_input(
        sex=sex,
        has_diabetes=has_diabetes,
        is_smoker=is_smoker,
        systolic_bp=systolic_bp,
        age=age,
        total_cholesterol=total_cholesterol,
    )

    age_bucket = get_age_bucket(age)

    if age_bucket is None:
        return {
            "is_applicable": False,
            "message": "No aplica: GLOBORISK se estima a partir de los 40 años.",
            "age_bucket": None,
            "systolic_bucket": None,
            "cholesterol_bucket": None,
            "risk_percent": None,
            "risk_display": None,
            "risk_category": None,
            "risk_category_label": None,
            "is_less_than_one": False,
        }

    systolic_bucket = get_systolic_bucket(systolic_bp)
    cholesterol_bucket = get_cholesterol_bucket(total_cholesterol)

    diabetes_key = "diabetic" if has_diabetes else "no_diabetic"
    smoker_key = "smoker" if is_smoker else "non_smoker"

    try:
        risk_cell = GLOBORISK_TABLE[sex][diabetes_key][smoker_key][age_bucket][systolic_bucket][cholesterol_bucket]
    except KeyError:
        raise GloboriskValidationError(
            "No se encontró una combinación válida para calcular el riesgo cardiovascular."
        )

    risk_percent = risk_cell["risk_percent"]
    is_less_than_one = risk_cell["is_less_than_one"]

    return {
        "is_applicable": True,
        "message": "Cálculo de riesgo cardiovascular realizado correctamente.",
        "age_bucket": age_bucket,
        "systolic_bucket": systolic_bucket,
        "cholesterol_bucket": cholesterol_bucket,
        "risk_percent": risk_percent,
        "risk_display": risk_cell["risk_display"],
        "risk_category": risk_cell["risk_category"],
        "risk_category_label": get_risk_category_label(
            risk_percent=risk_percent,
            is_less_than_one=is_less_than_one,
        ),
        "is_less_than_one": is_less_than_one,
    }