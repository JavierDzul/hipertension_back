from datetime import datetime
from app.extensions import db


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey("diseases.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    systolic = db.Column(db.Integer, nullable=False)
    diastolic = db.Column(db.Integer, nullable=False)

    symptoms_json = db.Column(db.JSON, nullable=False)
    risk_factors_json = db.Column(db.JSON, nullable=False)

    pressure_category = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(50), nullable=False)
    prediagnosis = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    matched_rules = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)