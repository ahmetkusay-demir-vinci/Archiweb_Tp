# Application Factory
import os
from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from .models import db, User
from .main.routes import main
from .auth.routes import auth

# LoginManager créé sans app, lié plus tard via login_manager.init_app(app)
login_manager = LoginManager()


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

    # Clé secrète utilisée pour signer les tokens JWT.
    # En production, cette valeur doit être longue, aléatoire et stockée dans une variable d'environnement.
    app.config['JWT_SECRET_KEY'] = 'changez-moi-en-production'

    # --- INITIALISATION des extensions ---
    # On lie db, login_manager et jwt à l'app (créés sans app dans leurs fichiers)
    db.init_app(app)
    login_manager.init_app(app)
    JWTManager(app)
    # Si un utilisateur non connecté accède à une page @login_required,
    # Flask-Login le redirige automatiquement vers cette route
    login_manager.login_view = 'auth.login'

    # user_loader : Flask-Login appelle cette fonction à chaque requête
    # pour recharger l'utilisateur depuis la DB à partir de son id stocké en session
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Création des tables si elles n'existent pas encore
    with app.app_context():
        db.create_all()

    # --- ENREGISTREMENT DES BLUEPRINTS ---
    # Import local pour éviter les imports circulaires (cf. cours slide 27)
    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Blueprint API : url_prefix déjà défini dans le Blueprint lui-même (/api/v1)
    from .api.routes import api
    app.register_blueprint(api)

    return app
