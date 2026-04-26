from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from app.models import db, FeatureRequest, User

# url_prefix='/api/v1' : toutes les routes ci-dessous seront préfixées automatiquement.
# Pourquoi versionner ? Si on casse le format de réponse demain, on crée /api/v2/
# pendant que /api/v1/ continue de fonctionner pour les anciens clients.
api = Blueprint('api', __name__, url_prefix='/api/v1')


def make_error(status_code, message, field=None):
    # Les clients d'une API attendent du JSON même en cas d'erreur, jamais du HTML.
    # 'field' est optionnel : utile pour indiquer quel champ est invalide.
    response = {'error': message, 'code': status_code}
    if field:
        response['field'] = field
    return jsonify(response), status_code


# ─── POST /api/v1/auth/token ── Obtention du token JWT ──────────────────────
# Le client envoie ses identifiants une seule fois. En retour il reçoit un token
# qu'il inclura dans toutes ses requêtes suivantes via le header :
#   Authorization: Bearer <token>

@api.route('/auth/token', methods=['POST'])
def get_token():
    data     = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    # On vérifie l'existence de l'utilisateur ET la validité du mot de passe en une condition.
    # check_password_hash compare le mot de passe en clair au hash stocké en base.
    if not user or not check_password_hash(user.password_hash, password):
        return make_error(401, 'Identifiants invalides')

    # identity : la valeur stockée dans le token, récupérable plus tard avec get_jwt_identity().
    # On stocke le username (string) plutôt que l'id pour que ce soit lisible.
    token = create_access_token(identity=username)
    return jsonify(access_token=token), 200


# ─── GET /api/v1/features ────────────────────────────────────────────────────
# Lecture publique : pas de @jwt_required() — tout le monde peut lire la liste.

@api.route('/features')
def get_features():
    nature = request.args.get('nature')
    status = request.args.get('status')
    sort   = request.args.get('sort', 'created_at')
    order  = request.args.get('order', 'desc')
    page     = request.args.get('page',     1,  type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = FeatureRequest.query

    if nature:
        query = query.filter_by(nature=nature)
    if status:
        query = query.filter_by(status=status)

    column = getattr(FeatureRequest, sort, None)
    if column:
        query = query.order_by(column.desc() if order == 'desc' else column.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total':    pagination.total,
        'page':     pagination.page,
        'pages':    pagination.pages,
        'per_page': pagination.per_page,
        'data':     [f.to_dict() for f in pagination.items],
    })


# ─── POST /api/v1/features ───────────────────────────────────────────────────
# @jwt_required() : Flask-JWT-Extended lit le header "Authorization: Bearer <token>",
# vérifie sa signature avec JWT_SECRET_KEY, et rejette la requête (401) si absent ou invalide.

@api.route('/features', methods=['POST'])
@jwt_required()
def create_feature():
    # get_jwt_identity() retourne la valeur stockée dans le token (le username, cf. get_token).
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()

    data = request.get_json() or {}
    if not data.get('title'):
        return make_error(400, 'Le titre est requis', 'title')

    feature = FeatureRequest(
        title=data['title'],
        description=data.get('description', ''),
        nature=data.get('nature', 'Feature'),
        priority=data.get('priority', 'Moyenne'),
        status='En attente',
        author_id=user.id  # On utilise l'id de l'utilisateur authentifié par le token
    )
    db.session.add(feature)
    db.session.commit()
    return jsonify(feature.to_dict()), 201


# ─── PUT /api/v1/features/<id> ── Remplacement total ────────────────────────

@api.route('/features/<int:id>', methods=['PUT'])
@jwt_required()
def update_feature_put(id):
    feature = FeatureRequest.query.get(id)
    if not feature:
        return make_error(404, 'Demande introuvable')

    data = request.get_json() or {}
    if not data.get('title'):
        return make_error(400, 'Le titre est requis pour un remplacement complet', 'title')

    feature.title       = data['title']
    feature.description = data.get('description', '')
    feature.nature      = data.get('nature', 'Feature')
    feature.priority    = data.get('priority', 'Moyenne')
    feature.status      = data.get('status', 'En attente')

    db.session.commit()
    return jsonify(feature.to_dict())


# ─── PATCH /api/v1/features/<id> ── Modification partielle ──────────────────

@api.route('/features/<int:id>', methods=['PATCH'])
@jwt_required()
def update_feature_patch(id):
    feature = FeatureRequest.query.get(id)
    if not feature:
        return make_error(404, 'Demande introuvable')

    data = request.get_json() or {}

    if 'title' in data:
        feature.title = data['title']
    if 'description' in data:
        feature.description = data['description']
    if 'nature' in data:
        feature.nature = data['nature']
    if 'priority' in data:
        feature.priority = data['priority']
    if 'status' in data:
        feature.status = data['status']

    db.session.commit()
    return jsonify(feature.to_dict())


# ─── DELETE /api/v1/features/<id> ────────────────────────────────────────────

@api.route('/features/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_feature(id):
    feature = FeatureRequest.query.get(id)
    if not feature:
        return make_error(404, 'Demande introuvable')

    db.session.delete(feature)
    db.session.commit()

    # 204 No Content : succès mais pas de corps de réponse (la ressource n'existe plus).
    # 200 impliquerait un corps — ici il n'y a rien à retourner.
    return '', 204


# ─── GET /api/v1/features/<id> ───────────────────────────────────────────────
# Lecture publique : pas de @jwt_required().

@api.route('/features/<int:id>')
def get_feature(id):
    feature = FeatureRequest.query.get(id)
    if not feature:
        return make_error(404, 'Demande introuvable')
    return jsonify(feature.to_dict())
