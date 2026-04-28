# app/models/medication.py

from datetime import datetime, timezone

from app.extensions import db


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(150), nullable=False)
    dose_mg = db.Column(db.Numeric(10, 2), nullable=False)
    frequency_hours = db.Column(db.Integer, nullable=False)
    first_dose_time = db.Column(db.Time, nullable=False)
    with_food = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    dose_logs = db.relationship(
        "MedicationDoseLog",
        back_populates="medication",
        cascade="all, delete-orphan",
    )

    user = db.relationship("User", back_populates="medications")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "dose_mg": float(self.dose_mg),
            "frequency_hours": self.frequency_hours,
            "first_dose_time": self.first_dose_time.strftime("%H:%M"),
            "with_food": self.with_food,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MedicationDoseLog(db.Model):
    __tablename__ = "medication_dose_logs"

    id = db.Column(db.Integer, primary_key=True)

    medication_id = db.Column(
        db.Integer,
        db.ForeignKey("medications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    scheduled_time = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    taken_at = db.Column(db.DateTime(timezone=True), nullable=True)

    status = db.Column(db.String(20), nullable=False, default="pending")
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    medication = db.relationship("Medication", back_populates="dose_logs")
    user = db.relationship("User", back_populates="medication_dose_logs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "user_id": self.user_id,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }