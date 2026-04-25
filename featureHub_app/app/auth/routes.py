from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import db, User

# Création du Blueprint "auth"
# Toutes les routes d'authentification seront préfixées par ce blueprint
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validation basique
        if not username or not password:
            flash("Nom d'utilisateur et mot de passe obligatoires.", "danger")
            return render_template('auth/register.html')

        # Vérifier si le nom d'utilisateur est déjà pris
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ce nom d'utilisateur est déjà pris.", "danger")
            return render_template('auth/register.html')

        # Créer le nouvel utilisateur (le mot de passe est hashé dans set_password)
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Compte créé ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Chercher l'utilisateur en base et vérifier le mot de passe
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # login_user() crée la session Flask-Login pour cet utilisateur
            login_user(user)
            flash(f"Bienvenue, {user.username} !", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    # logout_user() détruit la session Flask-Login
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for('main.index'))
