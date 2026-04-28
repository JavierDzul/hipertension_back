# app/models/medical_alert.py

from datetime import datetime, timezone

from app.extensions import db


class MedicalAlert(db.Model):
    __tablename__ = "medical_alerts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_type = db.Column(db.String(30), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)

    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    source = db.Column(db.String(150), nullable=True, index=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    resolved_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    user = db.relationship("User", back_populates="medical_alerts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "status": self.status,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }