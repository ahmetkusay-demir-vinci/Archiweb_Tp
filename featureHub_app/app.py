from datetime import datetime, timezone
from flask import Flask, render_template, abort, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'featurehub-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///featurehub.db'

db = SQLAlchemy(app)


# --- MODÉLISATION ---
class FeatureRequest(db.Model):
    __tablename__ = 'feature_requests'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status      = db.Column(db.String, default='En attente')
    nature      = db.Column(db.String, default='Feature')
    priority    = db.Column(db.String, default='Moyenne')
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<FeatureRequest {self.id}: {self.title}>' # Exemple : <FeatureRequest 1: Dark Mode>

# --- INITIALISATION ---
with app.app_context():
    db.create_all()

features_py = [
    {
        'id': 1,
        'title': 'Mode Sombre',
        'description': 'Ajouter un thème sombre à l\'interface.',
        'status': 'En attente',
        'nature': 'Feature',
        'priority': 'Haute'
    },
    {
        'id': 2,
        'title': 'Bug Login',
        'description': '',
        'status': 'Validé',
        'nature': 'Bug',
        'priority': 'Haute'
    },
    {
        'id': 3,
        'title': 'Améliorer les performances',
        'description': 'Optimiser les requêtes SQL.',
        'status': 'Rejeté',
        'nature': 'Amélioration',
        'priority': 'Moyenne'
    },
    {
        'id': 4,
        'title': 'Export CSV',
        'description': 'Permettre l\'export des données en CSV.',
        'status': 'En attente',
        'nature': 'Feature',
        'priority': 'Basse'
    }
]


@app.route('/')
def index():
    en_attente_py = sum(1 for f in features_py if f['status'] == 'En attente') # On ajoute +1 pour chaque feature en attente
    return render_template('index.html', features=features_py, en_attente=en_attente_py, active_page='index')


@app.route('/about')
def about():
    return render_template('about.html', active_page='about')


@app.route('/feature/<int:feature_id>')
def view_feature(feature_id):
    # Autre alternative, next() est un itérateur qui retourne le premier élément qui correspond ou None
    # feature = next((f for f in features_py if f['id'] == feature_id), None)
    feature = None
    for f in features_py:
        if f['id'] == feature_id:
            feature = f
            break
    if feature is None:
        abort(404)
    return render_template('view_feature.html', feature=feature, active_page='index')


@app.route('/feature/add', methods=['GET', 'POST'])
def add_feature():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        nature = request.form.get('nature', 'Feature')
        priority = request.form.get('priority', 'Moyenne')

        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template('add_feature.html', active_page='index')
        if len(title) > 100:
            flash("Le titre ne doit pas dépasser 100 caractères.", "danger")
            return render_template('add_feature.html', active_page='index')

        # Données valides — affichage temporaire dans la console
        print(f"Nouvelle demande : titre={title}, nature={nature}, priorité={priority}")

        flash("Demande ajoutée !", "success")
        return redirect(url_for('index'))

    return render_template('add_feature.html', active_page='index')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
