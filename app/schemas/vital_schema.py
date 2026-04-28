# app/schemas/vital_schema.py

from datetime import datetime, timezone

from app.system.hypertension_engine import SYMPTOMS


def parse_datetime_value(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("La fecha y hora deben tener formato ISO válido.")

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def validate_vital_payload(data: dict) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    required_fields = [
        "systolic_bp",
        "diastolic_bp",
        "heart_rate_bpm",
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"El campo '{field}' es obligatorio.")

    try:
        systolic_bp = int(data.get("systolic_bp"))
        diastolic_bp = int(data.get("diastolic_bp"))
        heart_rate_bpm = int(data.get("heart_rate_bpm"))
    except (TypeError, ValueError):
        raise ValueError("La presión y los latidos deben ser números enteros.")

    if systolic_bp < 70 or systolic_bp > 260:
        raise ValueError("La presión sistólica debe estar entre 70 y 260 mmHg.")

    if diastolic_bp < 40 or diastolic_bp > 160:
        raise ValueError("La presión diastólica debe estar entre 40 y 160 mmHg.")

    if heart_rate_bpm < 30 or heart_rate_bpm > 220:
        raise ValueError("Los latidos por minuto deben estar entre 30 y 220.")

    symptoms = data.get("symptoms", [])

    if symptoms is None:
        symptoms = []

    if not isinstance(symptoms, list):
        raise ValueError("Los síntomas deben enviarse como una lista.")

    invalid_symptoms = [
        symptom for symptom in symptoms
        if symptom not in SYMPTOMS
    ]

    if invalid_symptoms:
        raise ValueError(
            "Uno o más síntomas no son válidos."
        )

    recorded_at = data.get("recorded_at")

    if recorded_at:
        recorded_at = parse_datetime_value(str(recorded_at))
    else:
        recorded_at = datetime.now(timezone.utc)

    return {
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "heart_rate_bpm": heart_rate_bpm,
        "symptoms": symptoms,
        "recorded_at": recorded_at,
    }