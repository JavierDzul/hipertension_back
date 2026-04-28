# app/services/risk_service.py

from datetime import datetime, timezone

from app.extensions import db
from app.models.cardiovascular_risk import (
    CardiovascularRiskProfile,
    CardiovascularRiskHistory,
)
from app.system.globorisk_engine import calculate_globorisk, GloboriskValidationError


def get_user_risk_profile(user_id: int) -> CardiovascularRiskProfile | None:
    return CardiovascularRiskProfile.query.filter_by(user_id=user_id).first()


def get_user_risk_history(user_id: int, limit: int = 50) -> list[CardiovascularRiskHistory]:
    return (
        CardiovascularRiskHistory.query
        .filter_by(user_id=user_id)
        .order_by(CardiovascularRiskHistory.calculated_at.desc())
        .limit(limit)
        .all()
    )


def upsert_user_risk_profile(user_id: int, payload: dict) -> CardiovascularRiskProfile:
    try:
        result = calculate_globorisk(
            sex=payload["sex"],
            has_diabetes=payload["has_diabetes"],
            is_smoker=payload["is_smoker"],
            systolic_bp=payload["systolic_bp"],
            age=payload["age"],
            total_cholesterol=payload["total_cholesterol"],
        )
    except GloboriskValidationError:
        raise

    now = datetime.now(timezone.utc)

    profile = get_user_risk_profile(user_id)

    if profile is None:
        profile = CardiovascularRiskProfile(user_id=user_id)
        db.session.add(profile)

    profile.sex = payload["sex"]
    profile.has_diabetes = payload["has_diabetes"]
    profile.is_smoker = payload["is_smoker"]
    profile.systolic_bp = payload["systolic_bp"]
    profile.age = payload["age"]
    profile.total_cholesterol = payload["total_cholesterol"]

    profile.age_bucket = result["age_bucket"]
    profile.systolic_bucket = result["systolic_bucket"]
    profile.cholesterol_bucket = result["cholesterol_bucket"]

    profile.risk_percent = result["risk_percent"]
    profile.risk_display = result["risk_display"]
    profile.risk_category = result["risk_category"]
    profile.risk_category_label = result["risk_category_label"]

    profile.is_applicable = result["is_applicable"]
    profile.calculation_message = result["message"]
    profile.calculated_at = now

    history = CardiovascularRiskHistory(
        user_id=user_id,
        sex=payload["sex"],
        has_diabetes=payload["has_diabetes"],
        is_smoker=payload["is_smoker"],
        systolic_bp=payload["systolic_bp"],
        age=payload["age"],
        total_cholesterol=payload["total_cholesterol"],
        age_bucket=result["age_bucket"],
        systolic_bucket=result["systolic_bucket"],
        cholesterol_bucket=result["cholesterol_bucket"],
        risk_percent=result["risk_percent"],
        risk_display=result["risk_display"],
        risk_category=result["risk_category"],
        risk_category_label=result["risk_category_label"],
        is_applicable=result["is_applicable"],
        calculation_message=result["message"],
        calculated_at=now,
    )

    db.session.add(history)
    db.session.commit()

    
    from app.services.alert_service import create_alert_for_high_cardiovascular_risk

    create_alert_for_high_cardiovascular_risk(profile)

    return profile