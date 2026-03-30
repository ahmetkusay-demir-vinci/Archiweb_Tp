from flask import Flask, render_template, abort

app = Flask(__name__)

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
