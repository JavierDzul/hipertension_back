from app.extensions import db


class NotificationPreference(db.Model):
    __tablename__ = "notification_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    critical_alerts = db.Column(db.Boolean, default=True, nullable=False)
    ai_trends = db.Column(db.Boolean, default=True, nullable=False)
    medication_reminders = db.Column(db.Boolean, default=True, nullable=False)
    missed_doses = db.Column(db.Boolean, default=False, nullable=False)
    daily_measurement = db.Column(db.Boolean, default=True, nullable=False)
    health_tips = db.Column(db.Boolean, default=True, nullable=False)