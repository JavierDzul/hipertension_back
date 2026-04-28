# app/models/user.py

from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)

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

    risk_profile = db.relationship(
        "CardiovascularRiskProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    risk_history = db.relationship(
        "CardiovascularRiskHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    medications = db.relationship(
        "Medication",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    medication_dose_logs = db.relationship(
        "MedicationDoseLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    vital_records = db.relationship(
        "VitalRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    medical_alerts = db.relationship(
        "MedicalAlert",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }