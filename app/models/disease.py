from app.extensions import db


class Disease(db.Model):
    __tablename__ = "diseases"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    symptoms = db.relationship("Symptom", backref="disease", lazy=True)
    risk_factors = db.relationship("RiskFactor", backref="disease", lazy=True)
    evaluations = db.relationship("Evaluation", backref="disease", lazy=True)