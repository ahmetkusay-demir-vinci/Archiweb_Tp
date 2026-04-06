from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret123'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ============== 1. GET vs POST ==============

@app.route('/search', methods=['GET', 'POST'])
def search():
    """GET : données dans l'URL"""
    resultat = None
    if request.method == 'GET':
        query = request.args.get('query', '')
        if query:
            resultat = f"Résultats pour : {query}"
        else:
            resultat = "il n'y a aucun résultat"
    return render_template('search.html', resultat=resultat) 


# ============== 2. FORMULAIRE POST SIMPLE ==============

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """POST : données dans le body"""
    if request.method == 'POST':
        nom_py = request.form.get('nom') # nom, correspond au HTML, name="nom"
        email_py = request.form.get('email')
        
        # Validation côté serveur
        if not nom_py or len(nom_py) < 2:
            flash("Nom invalide !", "error")
            return redirect(url_for('contact')) # contact correspond à la fonction contact() et non à l'URL /contact
                                                # pattern PRG, redirection 302 après POST pour éviter les resoumissions de formulaire
        if '@' not in email_py:
            flash("Email invalide !", "error")
            return redirect(url_for('contact')) # contact correspond à la fonction contact()
        
        # POST-REDIRECT-GET pattern
        flash(f"Merci {nom_py}, votre email {email_py} a été reçu !", "success")
        return redirect(url_for('contact')) # contact correspond à la fonction contact()
    
    return render_template('contact.html')


# ============== 3. CHECKBOXES ==============

@app.route('/tags', methods=['GET', 'POST'])
def tags():
    """Checkboxes avec request.form.getlist()"""
    selected_tags = None
    if request.method == 'POST':
        # getlist() récupère TOUTES les checkboxes cochées
        selected_tags = request.form.getlist('tags')
        
        if not selected_tags:
            flash("Sélectionnez au moins un tag !", "error")
            return redirect(url_for('tags'))
        
        flash(f"Tags sélectionnés : {', '.join(selected_tags)}", "success")
        return redirect(url_for('tags'))
    
    return render_template('tags.html', selected_tags=selected_tags)


# ============== 4. VALIDATION & REQUÊTE COMPLEXE ==============

@app.route('/article', methods=['GET', 'POST'])
def article():
    """Validation complète d'un formulaire"""
    if request.method == 'POST':
        titre_py = request.form.get('titre', '').strip() # strip() pour enlever les espaces avant/après
        description_py = request.form.get('description', '').strip()
        categorie_py = request.form.get('categorie', '')
        
        # Validations
        errors = []
        if not titre_py or len(titre_py) < 3:
            errors.append("Titre trop court (min 3 caractères)")
        if not description_py or len(description_py) < 10:
            errors.append("Description trop courte (min 10 caractères)")
        if not categorie_py:
            errors.append("Catégorie obligatoire")
        
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for('article'))
        
        flash(f"Article '{titre_py}' publié en {categorie_py} !", "success")
        return redirect(url_for('article'))
    
    return render_template('article.html')


# ============== 5. UPLOAD DE FICHIERS ==============

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload avec secure_filename et vérification extension"""
    if request.method == 'POST':
        file = request.files.get('attachment')
        
        if not file or file.filename == '':
            flash("Pas de fichier sélectionné !", "error")
            return redirect(url_for('upload'))
        
        # Sécuriser le nom du fichier (évite ../../config.py)
        filename = secure_filename(file.filename)
        
        # Vérifier l'extension
        if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in {'jpg', 'png', 'pdf'}:
            flash("Extension non autorisée (jpg, png, pdf seulement) !", "error")
            return redirect(url_for('upload'))
        
        # Sauvegarder
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        flash(f"Fichier uploadé : {filename}", "success")
        return redirect(url_for('upload'))
    
    return render_template('upload.html')


# ============== 6. ACCUEIL ==============

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
