from app import create_app
from app.extensions import db
import app.models  # important so models are registered

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created successfully.")