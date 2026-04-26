from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models.disease import Disease
from app.models.evaluation import Evaluation
from app.system.knowledge_base import SYMPTOMS, RISK_FACTORS, DISEASE_CODE
from app.system.rule_engine import evaluate_case
from app.utils.serializers import serialize_evaluation

evaluation_bp = Blueprint("evaluations", __name__)


def validate_payload(data):
    required_fields = ["systolic", "diastolic", "symptoms", "risk_factors"]

    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"

    if not isinstance(data["systolic"], int) or data["systolic"] <= 0:
        return "systolic must be a positive integer"

    if not isinstance(data["diastolic"], int) or data["diastolic"] <= 0:
        return "diastolic must be a positive integer"

    if data["systolic"] < data["diastolic"]:
        return "systolic cannot be less than diastolic"

    if data["systolic"] > 350 or data["diastolic"] > 250:
        return "blood pressure values are out of allowed range"

    if not isinstance(data["symptoms"], list):
        return "symptoms must be a list"

    if not isinstance(data["risk_factors"], list):
        return "risk_factors must be a list"

    unknown_symptoms = [code for code in data["symptoms"] if code not in SYMPTOMS]
    if unknown_symptoms:
        return f"Unknown symptom codes: {', '.join(unknown_symptoms)}"

    unknown_risks = [code for code in data["risk_factors"] if code not in RISK_FACTORS]
    if unknown_risks:
        return f"Unknown risk factor codes: {', '.join(unknown_risks)}"

    return None


@evaluation_bp.post("/evaluations")
@jwt_required()
def create_evaluation():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    error = validate_payload(data)
    if error:
        return jsonify({"error": error}), 400

    disease = Disease.query.filter_by(code=DISEASE_CODE).first()
    if not disease:
        return jsonify({"error": "Disease seed data not found"}), 500

    result = evaluate_case(
        systolic=data["systolic"],
        diastolic=data["diastolic"],
        symptoms=data["symptoms"],
        risk_factors=data["risk_factors"],
    )

    evaluation = Evaluation(
        disease_id=disease.id,
        user_id=user_id,
        systolic=data["systolic"],
        diastolic=data["diastolic"],
        symptoms_json=data["symptoms"],
        risk_factors_json=data["risk_factors"],
        pressure_category=result["pressure_category"],
        risk_level=result["risk_level"],
        prediagnosis=result["prediagnosis"],
        recommendation=result["recommendation"],
        matched_rules=result["matched_rules"],
    )

    db.session.add(evaluation)
    db.session.commit()

    return jsonify({
        "message": "Evaluation created successfully",
        "evaluation": serialize_evaluation(evaluation),
    }), 201


@evaluation_bp.get("/evaluations")
@jwt_required()
def list_evaluations():
    user_id = int(get_jwt_identity())
    evaluations = (
        Evaluation.query.filter_by(user_id=user_id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )
    return jsonify([serialize_evaluation(e) for e in evaluations]), 200


@evaluation_bp.get("/evaluations/<int:evaluation_id>")
@jwt_required()
def get_evaluation(evaluation_id):
    user_id = int(get_jwt_identity())
    evaluation = Evaluation.query.filter_by(id=evaluation_id, user_id=user_id).first()

    if not evaluation:
        return jsonify({"error": "Evaluation not found"}), 404

    return jsonify(serialize_evaluation(evaluation)), 200