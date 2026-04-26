from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    profile = db.relationship("UserProfile", backref="user", uselist=False, cascade="all, delete-orphan")
    medications = db.relationship("Medication", backref="user", lazy=True, cascade="all, delete-orphan")
    contacts = db.relationship("EmergencyContact", backref="user", lazy=True, cascade="all, delete-orphan")
    notification_preferences = db.relationship(
        "NotificationPreference", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    evaluations = db.relationship("Evaluation", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()