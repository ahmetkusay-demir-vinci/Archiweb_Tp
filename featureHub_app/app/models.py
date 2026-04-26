# Modèles SQLAlchemy
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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
    author_id   = db.Column(db.Integer, db.ForeignKey('users.id')) # clé étrangère

    def __repr__(self):
        return f'<FeatureRequest {self.id}: {self.title}>'


# --- MODELE UTILISATEUR ---
# UserMixin fournit automatiquement les propriétés requises par Flask-Login :
# is_authenticated, is_active, is_anonymous, get_id()
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    features      = db.relationship('FeatureRequest', backref='author', lazy=True)

    # On ne stocke jamais le mot de passe en clair, seulement son hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Retourne True si le mot de passe fourni correspond au hash stocké
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
