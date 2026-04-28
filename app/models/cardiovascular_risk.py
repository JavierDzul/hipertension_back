# app/models/cardiovascular_risk.py

from datetime import datetime, timezone

from app.extensions import db


class CardiovascularRiskProfile(db.Model):
    __tablename__ = "cardiovascular_risk_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    sex = db.Column(db.String(20), nullable=False)
    has_diabetes = db.Column(db.Boolean, nullable=False)
    is_smoker = db.Column(db.Boolean, nullable=False)

    systolic_bp = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    total_cholesterol = db.Column(db.Integer, nullable=False)

    age_bucket = db.Column(db.Integer, nullable=True)
    systolic_bucket = db.Column(db.Integer, nullable=True)
    cholesterol_bucket = db.Column(db.Integer, nullable=True)

    risk_percent = db.Column(db.Float, nullable=True)
    risk_display = db.Column(db.String(20), nullable=True)
    risk_category = db.Column(db.String(50), nullable=True)
    risk_category_label = db.Column(db.String(100), nullable=True)

    is_applicable = db.Column(db.Boolean, nullable=False, default=True)
    calculation_message = db.Column(db.String(255), nullable=True)

    calculated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

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

    user = db.relationship(
        "User",
        back_populates="risk_profile",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sex": self.sex,
            "has_diabetes": self.has_diabetes,
            "is_smoker": self.is_smoker,
            "systolic_bp": self.systolic_bp,
            "age": self.age,
            "total_cholesterol": self.total_cholesterol,
            "age_bucket": self.age_bucket,
            "systolic_bucket": self.systolic_bucket,
            "cholesterol_bucket": self.cholesterol_bucket,
            "risk_percent": self.risk_percent,
            "risk_display": self.risk_display,
            "risk_category": self.risk_category,
            "risk_category_label": self.risk_category_label,
            "is_applicable": self.is_applicable,
            "calculation_message": self.calculation_message,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CardiovascularRiskHistory(db.Model):
    __tablename__ = "cardiovascular_risk_history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    sex = db.Column(db.String(20), nullable=False)
    has_diabetes = db.Column(db.Boolean, nullable=False)
    is_smoker = db.Column(db.Boolean, nullable=False)

    systolic_bp = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    total_cholesterol = db.Column(db.Integer, nullable=False)

    age_bucket = db.Column(db.Integer, nullable=True)
    systolic_bucket = db.Column(db.Integer, nullable=True)
    cholesterol_bucket = db.Column(db.Integer, nullable=True)

    risk_percent = db.Column(db.Float, nullable=True)
    risk_display = db.Column(db.String(20), nullable=True)
    risk_category = db.Column(db.String(50), nullable=True)
    risk_category_label = db.Column(db.String(100), nullable=True)

    is_applicable = db.Column(db.Boolean, nullable=False, default=True)
    calculation_message = db.Column(db.String(255), nullable=True)

    calculated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user = db.relationship(
        "User",
        back_populates="risk_history",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sex": self.sex,
            "has_diabetes": self.has_diabetes,
            "is_smoker": self.is_smoker,
            "systolic_bp": self.systolic_bp,
            "age": self.age,
            "total_cholesterol": self.total_cholesterol,
            "age_bucket": self.age_bucket,
            "systolic_bucket": self.systolic_bucket,
            "cholesterol_bucket": self.cholesterol_bucket,
            "risk_percent": self.risk_percent,
            "risk_display": self.risk_display,
            "risk_category": self.risk_category,
            "risk_category_label": self.risk_category_label,
            "is_applicable": self.is_applicable,
            "calculation_message": self.calculation_message,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }