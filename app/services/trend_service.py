# app/services/trend_service.py

from collections import Counter
from datetime import datetime, timedelta, timezone
from statistics import mean

from app.models.vital_record import VitalRecord


VALID_TREND_RANGES = {"day", "week", "month", "custom"}

DANGEROUS_CATEGORIES = {
    "grade_2",
    "grade_3",
    "isolated_systolic_hypertension",
}

ALARM_SYMPTOMS = {
    "chest_pain",
    "shortness_of_breath",
    "confusion",
    "weakness",
    "blurred_vision",
    "severe_headache",
}


class TrendError(Exception):
    def __init__(self, message: str, code: str = "TREND_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def parse_datetime_param(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise TrendError(
            message="Las fechas personalizadas deben tener formato ISO válido.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def get_period_range(range_type: str, start_date: str | None = None, end_date: str | None = None) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)

    if range_type not in VALID_TREND_RANGES:
        raise TrendError(
            message="El rango debe ser day, week, month o custom.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    if range_type == "day":
        return now - timedelta(days=1), now

    if range_type == "week":
        return now - timedelta(days=7), now

    if range_type == "month":
        return now - timedelta(days=30), now

    if not start_date or not end_date:
        raise TrendError(
            message="Para el rango custom debe enviar start_date y end_date.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    start = parse_datetime_param(start_date)
    end = parse_datetime_param(end_date)

    if start >= end:
        raise TrendError(
            message="La fecha inicial debe ser menor que la fecha final.",
            code="VALIDATION_ERROR",
            status_code=400,
        )

    return start, end


def get_previous_period_range(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    duration = end - start

    previous_end = start
    previous_start = start - duration

    return previous_start, previous_end


def get_records_in_range(user_id: int, start: datetime, end: datetime) -> list[VitalRecord]:
    return (
        VitalRecord.query
        .filter(
            VitalRecord.user_id == user_id,
            VitalRecord.recorded_at >= start,
            VitalRecord.recorded_at < end,
        )
        .order_by(VitalRecord.recorded_at.asc())
        .all()
    )


def safe_average(values: list[int]) -> float | None:
    if not values:
        return None

    return round(mean(values), 2)


def safe_min(values: list[int]) -> int | None:
    if not values:
        return None

    return min(values)


def safe_max(values: list[int]) -> int | None:
    if not values:
        return None

    return max(values)


def calculate_change(current_value: float | None, previous_value: float | None) -> float | None:
    if current_value is None or previous_value is None:
        return None

    return round(current_value - previous_value, 2)


def count_categories(records: list[VitalRecord]) -> dict:
    counter = Counter(record.bp_category for record in records)

    return dict(counter)


def count_symptoms(records: list[VitalRecord]) -> list[dict]:
    counter = Counter()

    for record in records:
        for symptom in record.symptoms or []:
            counter[symptom] += 1

    return [
        {
            "symptom": symptom,
            "count": count,
        }
        for symptom, count in counter.most_common()
    ]


def get_last_record(records: list[VitalRecord]) -> dict | None:
    if not records:
        return None

    return records[-1].to_dict()


def calculate_period_summary(records: list[VitalRecord]) -> dict:
    systolic_values = [record.systolic_bp for record in records]
    diastolic_values = [record.diastolic_bp for record in records]
    heart_rate_values = [record.heart_rate_bpm for record in records]

    return {
        "total_records": len(records),
        "average_systolic_bp": safe_average(systolic_values),
        "average_diastolic_bp": safe_average(diastolic_values),
        "average_heart_rate_bpm": safe_average(heart_rate_values),
        "min_systolic_bp": safe_min(systolic_values),
        "max_systolic_bp": safe_max(systolic_values),
        "min_diastolic_bp": safe_min(diastolic_values),
        "max_diastolic_bp": safe_max(diastolic_values),
        "min_heart_rate_bpm": safe_min(heart_rate_values),
        "max_heart_rate_bpm": safe_max(heart_rate_values),
        "category_counts": count_categories(records),
        "most_frequent_symptoms": count_symptoms(records),
        "last_record": get_last_record(records),
    }


def detect_dangerous_trends(
    current_records: list[VitalRecord],
    current_summary: dict,
    previous_summary: dict,
) -> list[dict]:
    trends = []

    dangerous_records_last_7_days = [
        record for record in current_records
        if record.bp_category in {"grade_2", "grade_3"}
    ]

    if len(dangerous_records_last_7_days) >= 3:
        trends.append({
            "type": "repeated_high_pressure",
            "severity": "high",
            "title": "Presión elevada repetida",
            "message": (
                "Se detectaron 3 o más registros en rangos de hipertensión grado II o III "
                "dentro del periodo revisado."
            ),
        })

    systolic_change = calculate_change(
        current_summary["average_systolic_bp"],
        previous_summary["average_systolic_bp"],
    )

    if systolic_change is not None and systolic_change >= 10:
        trends.append({
            "type": "systolic_increase",
            "severity": "high",
            "title": "Aumento de presión sistólica",
            "message": (
                f"El promedio de presión sistólica aumentó {systolic_change} mmHg "
                "comparado con el periodo anterior."
            ),
        })

    diastolic_change = calculate_change(
        current_summary["average_diastolic_bp"],
        previous_summary["average_diastolic_bp"],
    )

    if diastolic_change is not None and diastolic_change >= 5:
        trends.append({
            "type": "diastolic_increase",
            "severity": "high",
            "title": "Aumento de presión diastólica",
            "message": (
                f"El promedio de presión diastólica aumentó {diastolic_change} mmHg "
                "comparado con el periodo anterior."
            ),
        })

    average_heart_rate = current_summary["average_heart_rate_bpm"]

    if average_heart_rate is not None and average_heart_rate > 100:
        trends.append({
            "type": "high_average_heart_rate",
            "severity": "medium",
            "title": "Promedio de latidos elevado",
            "message": (
                f"El promedio de latidos fue de {average_heart_rate} bpm. "
                "Se recomienda repetir mediciones en reposo y consultar si se mantiene."
            ),
        })

    if average_heart_rate is not None and average_heart_rate < 50:
        trends.append({
            "type": "low_average_heart_rate",
            "severity": "medium",
            "title": "Promedio de latidos bajo",
            "message": (
                f"El promedio de latidos fue de {average_heart_rate} bpm. "
                "Consulte a un profesional de salud si presenta mareo, debilidad o desmayo."
            ),
        })

    records_with_alarm_symptoms_and_high_pressure = [
        record for record in current_records
        if record.bp_category in DANGEROUS_CATEGORIES
        and bool(set(record.symptoms or []).intersection(ALARM_SYMPTOMS))
    ]

    if records_with_alarm_symptoms_and_high_pressure:
        trends.append({
            "type": "alarm_symptoms_with_high_pressure",
            "severity": "critical",
            "title": "Síntomas de alarma con presión elevada",
            "message": (
                "Se detectaron síntomas de alarma junto con presión arterial elevada. "
                "Busque atención médica inmediata si presenta dolor en el pecho, falta de aire, "
                "confusión, debilidad, visión borrosa o dolor de cabeza intenso."
            ),
        })

    return trends


def create_alerts_for_dangerous_trends(
    user_id: int,
    dangerous_trends: list[dict],
    range_type: str,
    start: datetime,
    end: datetime,
) -> list[dict]:
    from app.services.alert_service import create_alert_if_not_exists

    created_alerts = []

    for trend in dangerous_trends:
        alert = create_alert_if_not_exists(
            user_id=user_id,
            alert_type="medical",
            severity=trend["severity"],
            title=trend["title"],
            message=trend["message"],
            source=(
                f"trend:{trend['type']}:"
                f"{range_type}:"
                f"{start.date().isoformat()}:"
                f"{end.date().isoformat()}"
            ),
        )

        created_alerts.append(alert.to_dict())

    return created_alerts


def get_vital_trends(
    user_id: int,
    range_type: str = "week",
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    current_start, current_end = get_period_range(
        range_type=range_type,
        start_date=start_date,
        end_date=end_date,
    )

    previous_start, previous_end = get_previous_period_range(current_start, current_end)

    current_records = get_records_in_range(user_id, current_start, current_end)
    previous_records = get_records_in_range(user_id, previous_start, previous_end)

    current_summary = calculate_period_summary(current_records)
    previous_summary = calculate_period_summary(previous_records)

    changes = {
        "average_systolic_bp_change": calculate_change(
            current_summary["average_systolic_bp"],
            previous_summary["average_systolic_bp"],
        ),
        "average_diastolic_bp_change": calculate_change(
            current_summary["average_diastolic_bp"],
            previous_summary["average_diastolic_bp"],
        ),
        "average_heart_rate_bpm_change": calculate_change(
            current_summary["average_heart_rate_bpm"],
            previous_summary["average_heart_rate_bpm"],
        ),
    }

    dangerous_trends = detect_dangerous_trends(
        current_records=current_records,
        current_summary=current_summary,
        previous_summary=previous_summary,
    )

    created_alerts = create_alerts_for_dangerous_trends(
        user_id=user_id,
        dangerous_trends=dangerous_trends,
        range_type=range_type,
        start=current_start,
        end=current_end,
    )

    return {
        "range": range_type,
        "current_period": {
            "start": current_start.isoformat(),
            "end": current_end.isoformat(),
        },
        "previous_period": {
            "start": previous_start.isoformat(),
            "end": previous_end.isoformat(),
        },
        "current_summary": current_summary,
        "previous_summary": previous_summary,
        "changes": changes,
        "dangerous_trends": dangerous_trends,
        "created_alerts": created_alerts,
    }