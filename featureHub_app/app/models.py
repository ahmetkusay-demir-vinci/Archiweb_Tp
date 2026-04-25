# Modèles SQLAlchemy
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# On crée db SANS l'application (pas de SQLAlchemy(app))
# Il sera lié à l'app plus tard via db.init_app(app) dans la factory
db = SQLAlchemy()


# --- MODELE ---
class FeatureRequest(db.Model):
    __tablename__ = 'feature_requests'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status      = db.Column(db.String, default='En attente')
    nature      = db.Column(db.String, default='Feature')
    priority    = db.Column(db.String, default='Moyenne')
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    filename    = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<FeatureRequest {self.id}: {self.title}>'
