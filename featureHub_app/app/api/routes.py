from flask import Blueprint, jsonify, request
from app.models import db, FeatureRequest

# url_prefix='/api/v1' : toutes les routes ci-dessous seront préfixées automatiquement.
# Pourquoi versionner ? Si on casse le format de réponse demain, on crée /api/v2/
# pendant que /api/v1/ continue de fonctionner pour les anciens clients.
api = Blueprint('api', __name__, url_prefix='/api/v1')


def make_error(status_code, message, field=None):
    # Les clients d'une API attendent du JSON même en cas d'erreur, jamais du HTML.
    # 'field' est optionnel : utile pour indiquer quel champ de formulaire est invalide.
    # Exemple : make_error(400, 'Titre obligatoire', field='title')
    # → {"error": "Titre obligatoire", "code": 400, "field": "title"}
    response = {'error': message, 'code': status_code}
    if field:
        response['field'] = field
    return jsonify(response), status_code


# ─── GET /api/v1/features ────────────────────────────────────────────────────

@api.route('/features')
def get_features():
    # --- Paramètres de filtrage ---
    # Contrairement à l'exo 1 (route web), ici on ne met PAS de valeur par défaut ''
    # pour pouvoir tester if nature: (None est falsy, '' aussi, mais c'est plus propre).
    nature = request.args.get('nature')
    status = request.args.get('status')

    # --- Paramètres de tri ---
    # 'sort' : nom de la colonne sur laquelle trier (ex: 'title', 'created_at', 'priority')
    # 'order' : 'desc' ou 'asc'
    sort  = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')

    # --- Paramètres de pagination ---
    page     = request.args.get('page',     1,  type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # --- Construction de la requête ---
    query = FeatureRequest.query

    # filter_by() est un raccourci de filter() pour les égalités simples.
    # filter_by(nature=nature) équivaut à filter(FeatureRequest.nature == nature).
    if nature:
        query = query.filter_by(nature=nature)
    if status:
        query = query.filter_by(status=status)

    # getattr(FeatureRequest, 'created_at', None) → retourne la colonne SQLAlchemy
    # FeatureRequest.created_at si elle existe, sinon None.
    # Cela évite une injection : on ne peut trier que sur de vraies colonnes du modèle.
    column = getattr(FeatureRequest, sort, None)
    if column:
        query = query.order_by(column.desc() if order == 'desc' else column.asc())

    # paginate() découpe les résultats en pages.
    # error_out=False : retourne une page vide au lieu d'un 404 si la page n'existe pas.
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total':    pagination.total,     # nombre total de résultats (toutes pages)
        'page':     pagination.page,      # numéro de la page courante
        'pages':    pagination.pages,     # nombre total de pages
        'per_page': pagination.per_page,  # taille d'une page
        'data':     [f.to_dict() for f in pagination.items],  # résultats de la page
    })


# ─── POST /api/v1/features ───────────────────────────────────────────────────

@api.route('/features', methods=['POST'])
def create_feature():
    # request.get_json() désérialise le corps de la requête (Content-Type: application/json).
    # Si le corps est vide ou non-JSON, retourne None → le `or {}` évite une erreur sur .get().
    data = request.get_json() or {}

    if not data.get('title'):
        return make_error(400, 'Le titre est requis', 'title')

    feature = FeatureRequest(
        title=data['title'],
        description=data.get('description', ''),
        nature=data.get('nature', 'Feature'),
        priority=data.get('priority', 'Moyenne'),
        status='En attente',
        author_id=1  # Remplacé en Exercice 5 par l'identité extraite du token JWT
    )
    db.session.add(feature)
    db.session.commit()

    # 201 Created : code standard pour une ressource créée avec succès.
    # On retourne la ressource créée pour que le client connaisse son id et created_at.
    return jsonify(feature.to_dict()), 201


# ─── GET /api/v1/features/<id> ───────────────────────────────────────────────

@api.route('/features/<int:id>')
def get_feature(id):
    feature = FeatureRequest.query.get(id)

    # On ne peut pas utiliser get_or_404() ici : il renverrait du HTML.
    # On gère le None manuellement pour rester en JSON.
    if not feature:
        return make_error(404, 'Demande introuvable')

    return jsonify(feature.to_dict())
