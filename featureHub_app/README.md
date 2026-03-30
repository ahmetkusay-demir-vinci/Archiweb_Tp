# FeatureHub

Application web de gestion et priorisation de demandes de fonctionnalités, développée avec Python et Flask.

## Technologies

- Python 3.x
- Flask
- Jinja2
- Bootstrap 5

## Installation

1. Cloner ou télécharger le projet
2. Créer un environnement virtuel :
   python -m venv venv
3. Activer l'environnement virtuel :
   .\venv\Scripts\activate
4. Installer les dépendances :
   pip install -r requirements.txt

## Lancement

python app.py

L'application est accessible sur : http://127.0.0.1:5000

## Structure du projet

featureHub_app/
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── view_feature.html
│   ├── 404.html
│   └── card.html
├── app.py
├── requirements.txt
└── README.md

## Fonctionnalités (TP1)

- Affichage des demandes sous forme de cartes Bootstrap
- Badges colorés par priorité et statut
- Page de détail par demande
- Page À propos
- Gestion d'erreur 404 personnalisée
- Navigation active dynamique
