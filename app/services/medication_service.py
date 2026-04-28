# app/services/medication_service.py

from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models.medication import Medication, MedicationDoseLog
from app.services.alert_service import create_medication_alert


class MedicationError(Exception):
    def __init__(self, message: str, code: str = "MEDICATION_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def get_user_medications(user_id: int) -> list[Medication]:
    return (
        Medication.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(Medication.created_at.desc())
        .all()
    )


def get_user_medication(user_id: int, medication_id: int) -> Medication:
    medication = (
        Medication.query
        .filter_by(id=medication_id, user_id=user_id, is_active=True)
        .first()
    )

    if not medication:
        raise MedicationError(
            message="Medicamento no encontrado.",
            code="MEDICATION_NOT_FOUND",
            status_code=404,
        )

    return medication


def create_medication(user_id: int, payload: dict) -> Medication:
    medication = Medication(
        user_id=user_id,
        name=payload["name"],
        dose_mg=payload["dose_mg"],
        frequency_hours=payload["frequency_hours"],
        first_dose_time=payload["first_dose_time"],
        with_food=payload["with_food"],
    )

    db.session.add(medication)
    db.session.commit()

    return medication


def update_medication(user_id: int, medication_id: int, payload: dict) -> Medication:
    medication = get_user_medication(user_id, medication_id)

    for field, value in payload.items():
        setattr(medication, field, value)

    db.session.commit()

    return medication


def delete_medication(user_id: int, medication_id: int) -> None:
    medication = get_user_medication(user_id, medication_id)

    medication.is_active = False
    db.session.commit()


def get_medication_dose_logs(
    user_id: int,
    medication_id: int,
    limit: int = 50,
) -> list[MedicationDoseLog]:
    get_user_medication(user_id, medication_id)

    return (
        MedicationDoseLog.query
        .filter_by(user_id=user_id, medication_id=medication_id)
        .order_by(MedicationDoseLog.scheduled_time.desc())
        .limit(limit)
        .all()
    )


def create_dose_log(
    user_id: int,
    medication_id: int,
    payload: dict,
) -> MedicationDoseLog:
    get_user_medication(user_id, medication_id)

    dose_log = MedicationDoseLog(
        user_id=user_id,
        medication_id=medication_id,
        scheduled_time=payload["scheduled_time"],
        taken_at=payload["taken_at"],
        status=payload["status"],
        notes=payload["notes"],
    )

    db.session.add(dose_log)
    db.session.commit()

    return dose_log


def get_logged_status_for_scheduled_time(
    user_id: int,
    medication_id: int,
    scheduled_time: datetime,
) -> str | None:
    start = scheduled_time - timedelta(minutes=2)
    end = scheduled_time + timedelta(minutes=2)

    dose_log = (
        MedicationDoseLog.query
        .filter(
            MedicationDoseLog.user_id == user_id,
            MedicationDoseLog.medication_id == medication_id,
            MedicationDoseLog.scheduled_time >= start,
            MedicationDoseLog.scheduled_time <= end,
        )
        .order_by(MedicationDoseLog.created_at.desc())
        .first()
    )

    return dose_log.status if dose_log else None


def calculate_schedule_status(
    medication: Medication,
    now: datetime | None = None,
) -> dict:
    if now is None:
        now = datetime.now(timezone.utc)

    first_today = datetime.combine(
        now.date(),
        medication.first_dose_time,
        tzinfo=timezone.utc,
    )

    frequency = timedelta(hours=medication.frequency_hours)

    scheduled_time = first_today

    while scheduled_time > now:
        scheduled_time -= frequency

    while scheduled_time + frequency <= now:
        scheduled_time += frequency

    previous_scheduled_time = scheduled_time
    next_scheduled_time = scheduled_time + frequency

    logged_status = get_logged_status_for_scheduled_time(
        user_id=medication.user_id,
        medication_id=medication.id,
        scheduled_time=previous_scheduled_time,
    )

    minutes_since_previous = (now - previous_scheduled_time).total_seconds() / 60
    minutes_until_next = (next_scheduled_time - now).total_seconds() / 60

    if logged_status in {"taken", "skipped", "missed"}:
        status = "completed"
        message = "La toma anterior ya fue registrada."
    elif 0 <= minutes_since_previous <= 30:
        status = "due"
        message = "La toma está pendiente en este momento."
    elif minutes_since_previous > 30:
        status = "missed"
        message = "La toma anterior parece estar vencida."
    elif minutes_until_next <= 120:
        status = "upcoming"
        message = "La próxima toma está cerca."
    else:
        status = "scheduled"
        message = "No hay una toma pendiente inmediata."

    return {
        "medication": medication.to_dict(),
        "status": status,
        "message": message,
        "previous_scheduled_time": previous_scheduled_time.isoformat(),
        "next_scheduled_time": next_scheduled_time.isoformat(),
        "logged_status": logged_status,
        "minutes_since_previous": round(minutes_since_previous, 2),
        "minutes_until_next": round(minutes_until_next, 2),
        "with_food_reminder": (
            "Este medicamento debe tomarse con alimentos."
            if medication.with_food
            else None
        ),
    }


def get_due_medications(user_id: int) -> list[dict]:
    medications = get_user_medications(user_id)
    results = []

    for medication in medications:
        schedule_status = calculate_schedule_status(medication)
        results.append(schedule_status)

        status = schedule_status["status"]
        scheduled_time = schedule_status["previous_scheduled_time"]

        if status == "due":
            create_medication_alert(
                user_id=user_id,
                medication_id=medication.id,
                severity="medium",
                title="Toma de medicamento pendiente",
                message=f"Está pendiente la toma de {medication.name}.",
                scheduled_time=scheduled_time,
            )

        if status == "missed":
            create_medication_alert(
                user_id=user_id,
                medication_id=medication.id,
                severity="high",
                title="Toma de medicamento omitida",
                message=f"La toma programada de {medication.name} parece estar vencida.",
                scheduled_time=scheduled_time,
            )

        if medication.with_food and status in {"due", "upcoming"}:
            create_medication_alert(
                user_id=user_id,
                medication_id=medication.id,
                severity="low",
                title="Medicamento con alimentos",
                message=f"{medication.name} debe tomarse con alimentos.",
                scheduled_time=scheduled_time,
            )

    return results