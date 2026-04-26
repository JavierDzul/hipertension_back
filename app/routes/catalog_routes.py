from flask import Blueprint, jsonify
from app.models.disease import Disease
from app.models.symptom import Symptom
from app.models.risk_factor import RiskFactor
from app.utils.serializers import (
    serialize_disease,
    serialize_symptom,
    serialize_risk_factor,
)

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.get("/diseases")
def get_diseases():
    diseases = Disease.query.order_by(Disease.id.asc()).all()
    return jsonify([serialize_disease(d) for d in diseases]), 200


@catalog_bp.get("/symptoms")
def get_symptoms():
    symptoms = Symptom.query.order_by(Symptom.id.asc()).all()
    return jsonify([serialize_symptom(s) for s in symptoms]), 200


@catalog_bp.get("/risk-factors")
def get_risk_factors():
    risk_factors = RiskFactor.query.order_by(RiskFactor.id.asc()).all()
    return jsonify([serialize_risk_factor(rf) for rf in risk_factors]), 200