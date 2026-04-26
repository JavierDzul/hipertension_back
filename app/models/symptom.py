from app.extensions import db


class Symptom(db.Model):
    __tablename__ = "symptoms"

    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey("diseases.id"), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    symptom_type = db.Column(db.String(50), nullable=False)
    is_alarm = db.Column(db.Boolean, default=False, nullable=False)