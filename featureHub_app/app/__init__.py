# Application Factory
import os
from flask import Flask
from .models import db
from .main.routes import main


# Cette fonctionne va configurer l'app et enregistrer les blueprints avant de la retourner
# L'appel de cette fonction se fait au sein de run.py
def create_app():
    app = Flask(__name__)

    # --- CONFIGURATION ---
    app.config['SECRET_KEY'] = 'featurehub-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///featurehub.db'

    # Configuration pour l'upload de fichiers
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 Mo max

    # --- INITIALISATION de la base de données ---
    # On lie db à l'app (db a été créé sans app dans models.py)
    db.init_app(app)

    # Création des tables si elles n'existent pas encore
    with app.app_context():
        db.create_all()

    # --- ENREGISTREMENT DES BLUEPRINTS ---
    # Import local pour éviter les imports circulaires (cf. cours slide 27)
    app.register_blueprint(main)

    return app
