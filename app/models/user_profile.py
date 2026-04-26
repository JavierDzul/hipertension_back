from app.extensions import db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    birth_date = db.Column(db.String(20))
    gender = db.Column(db.String(30))
    weight_kg = db.Column(db.String(20))
    height_m = db.Column(db.String(20))
    blood_type = db.Column(db.String(20))
    diagnosis = db.Column(db.String(150))
    diagnosis_notes = db.Column(db.Text)