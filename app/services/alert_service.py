# app/services/alert_service.py

from datetime import datetime, timezone

from app.extensions import db
from app.models.medical_alert import MedicalAlert


class AlertError(Exception):
    def __init__(self, message: str, code: str = "ALERT_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def get_user_alerts(
    user_id: int,
    status: str | None = "active",
    limit: int = 50,
) -> list[MedicalAlert]:
    query = MedicalAlert.query.filter_by(user_id=user_id)

    if status:
        query = query.filter_by(status=status)

    return (
        query
        .order_by(MedicalAlert.created_at.desc())
        .limit(limit)
        .all()
    )


def get_user_alert(user_id: int, alert_id: int) -> MedicalAlert:
    alert = MedicalAlert.query.filter_by(id=alert_id, user_id=user_id).first()

    if not alert:
        raise AlertError(
            message="Alerta no encontrada.",
            code="ALERT_NOT_FOUND",
            status_code=404,
        )

    return alert


def create_alert(
    user_id: int,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    source: str | None = None,
) -> MedicalAlert:
    alert = MedicalAlert(
        user_id=user_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        source=source,
    )

    db.session.add(alert)
    db.session.commit()

    return alert


def create_alert_if_not_exists(
    user_id: int,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    source: str,
) -> MedicalAlert:
    existing_alert = (
        MedicalAlert.query
        .filter_by(
            user_id=user_id,
            alert_type=alert_type,
            source=source,
            status="active",
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    return create_alert(
        user_id=user_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        source=source,
    )


def resolve_alert(user_id: int, alert_id: int) -> MedicalAlert:
    alert = get_user_alert(user_id, alert_id)

    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)

    db.session.commit()

    return alert


def dismiss_alert(user_id: int, alert_id: int) -> MedicalAlert:
    alert = get_user_alert(user_id, alert_id)

    alert.status = "dismissed"
    alert.resolved_at = datetime.now(timezone.utc)

    db.session.commit()

    return alert


def create_alerts_for_vital_record(vital_record) -> list[MedicalAlert]:
    created_alerts = []

    if vital_record.bp_category == "grade_3":
        alert = create_alert_if_not_exists(
            user_id=vital_record.user_id,
            alert_type="medical",
            severity="critical",
            title="Presión arterial muy alta",
            message=(
                "La evaluación inicial detectó presión arterial en rango de hipertensión grado III. "
                "Busque atención médica inmediata si la medición se mantiene elevada o presenta síntomas de alarma."
            ),
            source=f"vital_record:{vital_record.id}:grade_3",
        )
        created_alerts.append(alert)

    if vital_record.bp_category == "grade_2":
        alert = create_alert_if_not_exists(
            user_id=vital_record.user_id,
            alert_type="medical",
            severity="high",
            title="Presión arterial elevada",
            message=(
                "La evaluación inicial detectó presión arterial en rango de hipertensión grado II. "
                "Se recomienda seguimiento con un profesional de salud."
            ),
            source=f"vital_record:{vital_record.id}:grade_2",
        )
        created_alerts.append(alert)

    if vital_record.has_alarm_symptoms:
        alert = create_alert_if_not_exists(
            user_id=vital_record.user_id,
            alert_type="medical",
            severity="critical",
            title="Síntomas de alarma registrados",
            message=(
                "Se registraron síntomas de alarma asociados a la presión arterial. "
                "Busque atención médica inmediata si presenta dolor en el pecho, falta de aire, confusión, debilidad, visión borrosa o dolor de cabeza intenso."
            ),
            source=f"vital_record:{vital_record.id}:alarm_symptoms",
        )
        created_alerts.append(alert)

    if vital_record.heart_rate_bpm > 100:
        alert = create_alert_if_not_exists(
            user_id=vital_record.user_id,
            alert_type="medical",
            severity="medium",
            title="Latidos elevados",
            message=(
                "Se registraron latidos por minuto elevados. "
                "Repita la medición en reposo y consulte si se mantiene."
            ),
            source=f"vital_record:{vital_record.id}:high_heart_rate",
        )
        created_alerts.append(alert)

    if vital_record.heart_rate_bpm < 50:
        alert = create_alert_if_not_exists(
            user_id=vital_record.user_id,
            alert_type="medical",
            severity="medium",
            title="Latidos bajos",
            message=(
                "Se registraron latidos por minuto bajos. "
                "Consulte a un profesional de salud si presenta mareo, debilidad o desmayo."
            ),
            source=f"vital_record:{vital_record.id}:low_heart_rate",
        )
        created_alerts.append(alert)

    return created_alerts


def create_alert_for_high_cardiovascular_risk(risk_profile) -> MedicalAlert | None:
    if risk_profile.risk_percent is None:
        return None

    if risk_profile.risk_percent < 10:
        return None

    severity = "critical" if risk_profile.risk_percent >= 15 else "high"

    return create_alert_if_not_exists(
        user_id=risk_profile.user_id,
        alert_type="medical",
        severity=severity,
        title="Riesgo cardiovascular elevado",
        message=(
            f"El cálculo GLOBORISK estimó un riesgo cardiovascular a 10 años de {risk_profile.risk_display}. "
            "Se recomienda consultar a un profesional de salud para seguimiento."
        ),
        source=f"risk_profile:{risk_profile.id}:high_risk",
    )


def create_medication_alert(
    user_id: int,
    medication_id: int,
    severity: str,
    title: str,
    message: str,
    scheduled_time: str,
) -> MedicalAlert:
    return create_alert_if_not_exists(
        user_id=user_id,
        alert_type="medication",
        severity=severity,
        title=title,
        message=message,
        source=f"medication:{medication_id}:scheduled:{scheduled_time}",
    )