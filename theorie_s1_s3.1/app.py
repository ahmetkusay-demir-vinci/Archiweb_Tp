from flask import Flask, request, url_for, render_template
app = Flask(__name__)


@app.route("/")
def home():
    return render_template('index.html')


@app.route('/2')
def template_example():
    # Flask cherche automatiquement dans le dossier 'templates/'
    return render_template(
        'index.html',
        title="Ma Page",
        user={"name": "Alice"},
        items=["Pomme", "Banane", "Cerise"]
    )


@app.route("/contacts")
def contact():
    return "Contactez-nous à support@example.com"


@app.route("/user/<username>") #/user/kusay dans l'URL
def show_user(username):
    return f"Profil de {username}"


@app.route('/3')
def index(): #url_for, va rediriger l'url vers un autre
    return f'Voir le profil de <a href="{url_for("show_user", username="kusay")}">Ahmet Kusay Demir</a>' 


@app.route('/post/<int:post_id>') # forcer le type de variable (str, int, float, path, uuid)
def show_post(post_id):
    return f"Article numéro {post_id}"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # request.form.get permet de récupérer les données du formulaire envoyé en POST
        x_username = request.form.get('username')
        x_password = request.form.get('password')
        
        if x_username == "admin" and x_password == "secret":
            return f"Bienvenue {x_username}, vous êtes connecté !"
        return "Identifiants invalides", 401
    
    # Pour GET, afficher le formulaire de connexion
    return render_template('login.html')


@app.errorhandler(404)
def page_not_found(error):
    return "Cette ressource n'existe pas.", 404


@app.route('/produits')
def produits():
    # Exemple avec données dynamiques
    produit_list = [
        {'nom': 'Laptop', 'prix': 999, 'stock': 5},
        {'nom': 'Souris', 'prix': 29, 'stock': 15},
        {'nom': 'Clavier', 'prix': 89, 'stock': 0},
    ]
    user_name = "Alice"
    total_prix = sum(p['prix'] for p in produit_list)
    
    return render_template('produits.html', 
                         produits=produit_list, 
                         user=user_name,
                         total=total_prix)


@app.route('/filters')
def filters_demo():
    # Données pour illustrer les filtres Jinja2
    x_ville = "bruxelles"
    x_description = "Une superbe fonctionnalité qui permet de transformer les données facilement et rapidement."
    x_fruits = ["banane", "pomme", "cerise", "abricot"]
    x_produits_with_prix = [
        {'nom': 'Chaise', 'prix': 45},
        {'nom': 'Table', 'prix': 120},
        {'nom': 'Lampe', 'prix': 35},
    ]
    x_auteur = "kusay"  # Démonstration du filtre default
    
    return render_template('filters.html',
                         ville=x_ville,
                         description=x_description,
                         fruits=x_fruits,
                         produits_with_prix=x_produits_with_prix,
                         auteur=x_auteur)


if __name__ == "__main__":
    app.run(debug=True)
