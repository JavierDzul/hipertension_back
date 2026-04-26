from app import create_app
from app.extensions import db
from app.models.disease import Disease
from app.models.symptom import Symptom
from app.models.risk_factor import RiskFactor
from app.system.knowledge_base import DISEASE_CODE, SYMPTOMS, RISK_FACTORS

app = create_app()

with app.app_context():
    disease = Disease.query.filter_by(code=DISEASE_CODE).first()

    if not disease:
        disease = Disease(
            code=DISEASE_CODE,
            name="Riesgo cardiovascular asociado a hipertensión",
            description="Prediagnóstico basado en presión arterial, síntomas y factores de riesgo cardiovascular."
        )
        db.session.add(disease)
        db.session.commit()

    for code, symptom_data in SYMPTOMS.items():
        existing = Symptom.query.filter_by(code=code).first()
        if not existing:
            symptom = Symptom(
                disease_id=disease.id,
                code=code,
                name=symptom_data["name"],
                description=symptom_data["description"],
                symptom_type=symptom_data["type"],
                is_alarm=symptom_data["is_alarm"],
            )
            db.session.add(symptom)

    for code, risk_factor_data in RISK_FACTORS.items():
        existing = RiskFactor.query.filter_by(code=code).first()
        if not existing:
            risk_factor = RiskFactor(
                disease_id=disease.id,
                code=code,
                name=risk_factor_data["name"],
                description=risk_factor_data["description"],
            )
            db.session.add(risk_factor)

    db.session.commit()
    print("Seed data inserted successfully.")