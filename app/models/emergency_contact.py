from app.extensions import db


class EmergencyContact(db.Model):
    __tablename__ = "emergency_contacts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    full_name = db.Column(db.String(150), nullable=False)
    relationship = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(40), nullable=False)