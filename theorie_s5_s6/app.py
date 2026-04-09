from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

# --- MODÉLISATION ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    # Ajout du cascade : si on supprime un user, ses features sont supprimées 
    features = db.relationship('Feature', backref='author', cascade='all, delete-orphan')

class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# --- INITIALISATION ---
with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add(User(username="Kusay"))
        db.session.commit()

# ==========================================
# ROUTES : CRUD USER
# ==========================================

@app.route('/')
def index():
    # READ : Affiche tous les users
    users = User.query.all()
    return render_template('index.html', users=users) #users en orange correspond au HTML {% for user in users %}

@app.route('/add_user', methods=['POST'])
def add_user():
    # CREATE : Ajoute un nouvel utilisateur
    username = request.form.get('username') # 'username' correspond au HTML name="username" du formulaire
    nouveau_user = User(username=username) 
    db.session.add(nouveau_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_user/<int:id>', methods=['POST'])
def update_user(id):
    # UPDATE : Modifie le nom d'un utilisateur existant
    user = User.query.get(id)
    if user:
        user.username = request.form.get('new_username')
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    # DELETE : Supprime un utilisateur (et ses features grâce au cascade)
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('index'))


# ==========================================
# ROUTES : FEATURES (Liées à un User)
# ==========================================

@app.route('/add_feature/<int:user_id>', methods=['POST'])
def add_feature(user_id):
    # CREATE : Ajoute une feature pour un utilisateur SPÉCIFIQUE
    titre = request.form.get('title')
    user = User.query.get(user_id) # On récupère le bon user
    
    if user:
        nouvelle_feature = Feature(title=titre, author=user)
        db.session.add(nouvelle_feature)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/delete_feature/<int:id>')
def delete_feature(id):
    # DELETE : Supprime une feature spécifique
    feature = Feature.query.get(id)
    if feature:
        db.session.delete(feature)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
