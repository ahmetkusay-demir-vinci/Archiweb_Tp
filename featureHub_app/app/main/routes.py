import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, FeatureRequest

# Création du Blueprint "main" (cf. cours slide 23)
# Remplace @app.route par @main.route
main = Blueprint('main', __name__)

# Extensions autorisées pour l'upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- ROUTES ---

@main.route('/')
def index():
    features = FeatureRequest.query.order_by(FeatureRequest.created_at.desc()).all()
    en_attente = sum(1 for f in features if f.status == 'En attente')
    return render_template('main/index.html', features=features, en_attente=en_attente, active_page='index')


@main.route('/about')
def about():
    return render_template('main/about.html', active_page='about')


@main.route('/feature/<int:feature_id>')
def view_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)
    return render_template('main/view_feature.html', feature=feature, active_page='index')


@main.route('/feature/add', methods=['GET', 'POST'])
@login_required
def add_feature():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        nature = request.form.get('nature', 'Feature')
        priority = request.form.get('priority', 'Moyenne')

        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template('main/add_feature.html', active_page='index')
        if len(title) > 100:
            flash("Le titre ne doit pas dépasser 100 caractères.", "danger")
            return render_template('main/add_feature.html', active_page='index')

        # Gestion du fichier joint
        saved_filename = None
        file = request.files.get('file')
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Extension non autorisée (png, jpg, jpeg, gif, pdf uniquement).", "danger")
                return render_template('main/add_feature.html', active_page='index')
            saved_filename = secure_filename(file.filename)
            # current_app remplace "app" pour accéder à la config dans un Blueprint
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename))

        new_feature = FeatureRequest(
            title=title,
            description=description,
            nature=nature,
            priority=priority,
            filename=saved_filename,
            #Lors de la création de la feature, on associe direct à l'utilisateur connecté
            author_id=current_user.id 
        )
        try:
            db.session.add(new_feature)
            db.session.commit()
            flash("Demande ajoutée !", "success")
        except Exception:
            db.session.rollback()
            flash("Erreur lors de l'enregistrement.", "danger")
        return redirect(url_for('main.index'))

    return render_template('main/add_feature.html', active_page='index')


@main.route('/feature/<int:feature_id>/edit', methods=['GET', 'POST'])
def edit_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        nature = request.form.get('nature', feature.nature)
        priority = request.form.get('priority', feature.priority)
        status = request.form.get('status', feature.status)

        if not title:
            flash("Le titre est obligatoire.", "danger")
            return render_template('main/edit_feature.html', feature=feature, active_page='index')
        if len(title) > 100:
            flash("Le titre ne doit pas dépasser 100 caractères.", "danger")
            return render_template('main/edit_feature.html', feature=feature, active_page='index')

        # Mise à jour des attributs de l'objet
        feature.title       = title
        feature.description = description
        feature.nature      = nature
        feature.priority    = priority
        feature.status      = status

        try:
            db.session.commit()
            flash("Demande modifiée !", "success")
        except Exception:
            db.session.rollback()
            flash("Erreur lors de la modification.", "danger")
        return redirect(url_for('main.view_feature', feature_id=feature.id))

    return render_template('main/edit_feature.html', feature=feature, active_page='index')


@main.route('/feature/<int:feature_id>/delete', methods=['POST'])
def delete_feature(feature_id):
    feature = FeatureRequest.query.get_or_404(feature_id)
    try:
        db.session.delete(feature)
        db.session.commit()
        flash(f"Demande « {feature.title} » supprimée.", "success")
    except Exception:
        db.session.rollback()
        flash("Erreur lors de la suppression.", "danger")
    return redirect(url_for('main.index'))


# --- GESTION D'ERREUR ---
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
