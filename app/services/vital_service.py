# app/services/vital_service.py

from datetime import datetime, timezone

from app.extensions import db
from app.models.vital_record import VitalRecord
from app.system.hypertension_engine import evaluate_hypertension_case, SYMPTOMS


class VitalRecordError(Exception):
    def __init__(self, message: str, code: str = "VITAL_RECORD_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def create_vital_record(user_id: int, payload: dict) -> VitalRecord:
    evaluation = evaluate_hypertension_case(
        systolic_bp=payload["systolic_bp"],
        diastolic_bp=payload["diastolic_bp"],
        heart_rate_bpm=payload["heart_rate_bpm"],
        symptoms=payload["symptoms"],
    )

    vital_record = VitalRecord(
        user_id=user_id,
        systolic_bp=payload["systolic_bp"],
        diastolic_bp=payload["diastolic_bp"],
        heart_rate_bpm=payload["heart_rate_bpm"],
        symptoms=evaluation["symptoms"],
        symptom_labels=evaluation["symptom_labels"],
        bp_category=evaluation["bp_category"],
        bp_category_label=evaluation["bp_category_label"],
        systolic_category=evaluation["systolic_category"],
        diastolic_category=evaluation["diastolic_category"],
        is_isolated_systolic=evaluation["is_isolated_systolic"],
        has_alarm_symptoms=evaluation["has_alarm_symptoms"],
        urgency_level=evaluation["urgency_level"],
        initial_assessment=evaluation["initial_assessment"],
        recommendations=evaluation["recommendations"],
        recorded_at=payload.get("recorded_at", datetime.now(timezone.utc)),
    )

    db.session.add(vital_record)
    db.session.commit()

    from app.services.alert_service import create_alerts_for_vital_record

    create_alerts_for_vital_record(vital_record)

    return vital_record


def get_user_vital_records(
    user_id: int,
    limit: int = 50,
) -> list[VitalRecord]:
    return (
        VitalRecord.query
        .filter_by(user_id=user_id)
        .order_by(VitalRecord.recorded_at.desc())
        .limit(limit)
        .all()
    )


def get_user_vital_record(user_id: int, record_id: int) -> VitalRecord:
    record = (
        VitalRecord.query
        .filter_by(id=record_id, user_id=user_id)
        .first()
    )

    if not record:
        raise VitalRecordError(
            message="Registro de signos vitales no encontrado.",
            code="VITAL_RECORD_NOT_FOUND",
            status_code=404,
        )

    return record


def get_available_symptoms() -> list[dict]:
    return [
        {
            "key": key,
            "label": label,
        }
        for key, label in SYMPTOMS.items()
    ]