# app/schemas/medication_schema.py

from datetime import datetime, time, timezone


VALID_DOSE_STATUSES = {"pending", "taken", "skipped", "missed"}


def parse_time_value(value: str) -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError("El horario de primera toma debe tener formato HH:MM.")


def parse_datetime_value(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("La fecha y hora deben tener formato ISO válido.")

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def validate_medication_payload(data: dict, partial: bool = False) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    required_fields = [
        "name",
        "dose_mg",
        "frequency_hours",
        "first_dose_time",
        "with_food",
    ]

    if not partial:
        for field in required_fields:
            if field not in data:
                raise ValueError(f"El campo '{field}' es obligatorio.")

    payload = {}

    if "name" in data:
        name = str(data.get("name", "")).strip()

        if len(name) < 2:
            raise ValueError("El nombre del medicamento debe tener al menos 2 caracteres.")

        payload["name"] = name

    if "dose_mg" in data:
        try:
            dose_mg = float(data.get("dose_mg"))
        except (TypeError, ValueError):
            raise ValueError("La dosis debe ser un número válido.")

        if dose_mg <= 0:
            raise ValueError("La dosis debe ser mayor a 0 mg.")

        payload["dose_mg"] = dose_mg

    if "frequency_hours" in data:
        try:
            frequency_hours = int(data.get("frequency_hours"))
        except (TypeError, ValueError):
            raise ValueError("La frecuencia debe ser un número entero.")

        if frequency_hours <= 0:
            raise ValueError("La frecuencia debe ser mayor a 0 horas.")

        if frequency_hours > 168:
            raise ValueError("La frecuencia no puede ser mayor a 168 horas.")

        payload["frequency_hours"] = frequency_hours

    if "first_dose_time" in data:
        payload["first_dose_time"] = parse_time_value(str(data.get("first_dose_time")))

    if "with_food" in data:
        with_food = data.get("with_food")

        if not isinstance(with_food, bool):
            raise ValueError("El campo 'with_food' debe ser verdadero o falso.")

        payload["with_food"] = with_food

    return payload


def validate_dose_log_payload(data: dict) -> dict:
    if not data:
        raise ValueError("El cuerpo de la solicitud es obligatorio.")

    status = data.get("status")

    if status not in VALID_DOSE_STATUSES:
        raise ValueError("El estado de la toma debe ser pending, taken, skipped o missed.")

    scheduled_time = data.get("scheduled_time")
    taken_at = data.get("taken_at")
    notes = data.get("notes")

    if scheduled_time:
        scheduled_time = parse_datetime_value(str(scheduled_time))
    else:
        scheduled_time = datetime.now(timezone.utc)

    if taken_at:
        taken_at = parse_datetime_value(str(taken_at))
    elif status == "taken":
        taken_at = datetime.now(timezone.utc)
    else:
        taken_at = None

    return {
        "scheduled_time": scheduled_time,
        "taken_at": taken_at,
        "status": status,
        "notes": str(notes).strip() if notes else None,
    }