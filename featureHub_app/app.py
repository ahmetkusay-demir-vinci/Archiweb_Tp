from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
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


@app.route('/')
def index():
    features = FeatureRequest.query.order_by(FeatureRequest.created_at.desc()).all()
    en_attente = sum(1 for f in features if f.status == 'En attente')
    return render_template('index.html', features=features, en_attente=en_attente, active_page='index') #features en orange correspond à la variable features dans index.html


@app.route('/about')
def about():
    return render_template('about.html', active_page='about')


@app.route('/feature/<int:feature_id>')
def view_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)
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

        new_feature = FeatureRequest(
            title=title,
            description=description,
            nature=nature,
            priority=priority
        )
        try:
            db.session.add(new_feature)
            db.session.commit()
            flash("Demande ajoutée !", "success")
        except Exception:
            db.session.rollback()
            flash("Erreur lors de l'enregistrement.", "danger")
        return redirect(url_for('index'))

    return render_template('add_feature.html', active_page='index')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
