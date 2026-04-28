# app/models/vital_record.py

from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class VitalRecord(db.Model):
    __tablename__ = "vital_records"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    systolic_bp = db.Column(db.Integer, nullable=False)
    diastolic_bp = db.Column(db.Integer, nullable=False)
    heart_rate_bpm = db.Column(db.Integer, nullable=False)

    symptoms = db.Column(JSONB, nullable=False, default=list)
    symptom_labels = db.Column(JSONB, nullable=False, default=list)

    bp_category = db.Column(db.String(60), nullable=False, index=True)
    bp_category_label = db.Column(db.String(100), nullable=False)

    systolic_category = db.Column(db.String(60), nullable=False)
    diastolic_category = db.Column(db.String(60), nullable=False)

    is_isolated_systolic = db.Column(db.Boolean, nullable=False, default=False)
    has_alarm_symptoms = db.Column(db.Boolean, nullable=False, default=False)
    urgency_level = db.Column(db.String(20), nullable=False, default="low")

    initial_assessment = db.Column(db.Text, nullable=False)
    recommendations = db.Column(JSONB, nullable=False, default=list)

    recorded_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = db.relationship("User", back_populates="vital_records")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "heart_rate_bpm": self.heart_rate_bpm,
            "symptoms": self.symptoms,
            "symptom_labels": self.symptom_labels,
            "bp_category": self.bp_category,
            "bp_category_label": self.bp_category_label,
            "systolic_category": self.systolic_category,
            "diastolic_category": self.diastolic_category,
            "is_isolated_systolic": self.is_isolated_systolic,
            "has_alarm_symptoms": self.has_alarm_symptoms,
            "urgency_level": self.urgency_level,
            "initial_assessment": self.initial_assessment,
            "recommendations": self.recommendations,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }