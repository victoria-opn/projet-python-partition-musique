# Partition Musique

Transcrire un morceau à l'oreille puis le transposer prend du temps : cette application web Django transforme un fichier audio en partition PDF transposée dans la tonalité choisie, avec un suivi du traitement en temps réel.

Le détail du projet (besoin, fonctionnalités, répartition des tâches, planning, MVP et paliers) est dans le [cahier des charges](cahier_des_charges_projet_python.md).

## Lancer le projet

```bash
git clone https://github.com/victoria-opn/projet-python-partition-musique.git
cd projet-python-partition-musique
cp .env.example .env
# Renseigner les mots de passe et la clé secrète dans .env avant de continuer.
docker compose up -d
```

Sous Windows PowerShell, remplace `cp .env.example .env` par `Copy-Item .env.example .env`.
Compose crée le superutilisateur Django à partir de `DJANGO_SUPERUSER_USERNAME` et
`DJANGO_SUPERUSER_PASSWORD` dans `.env` ; si ce compte existe déjà, son mot de passe
n'est pas modifié.

Le site répond sur http://localhost:8080.

### Publier l'image sur GitHub Container Registry

Après avoir installé Docker Desktop et créé un Personal Access Token GitHub avec
`write:packages`, connecte-toi puis construis et publie l'image :

```powershell
docker login ghcr.io -u victoria-opn
docker compose build web
docker compose push web
```

Docker demande le token comme mot de passe. L'image est publiée sous
`ghcr.io/victoria-opn/projet-python-partition-musique:latest`. Pour publier une
version identifiée, modifie le tag `image` dans `docker-compose.yml` avant de
construire et pousser.

> La conteneurisation est en cours : en attendant, le projet se lance en local (voir ci-dessous).

### En local (développement)

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_user('user', password='musique-demo-2026')"
python manage.py runserver
```

Compte de démonstration local : `user` / `musique-demo-2026`. Ne pas réutiliser ce mot de passe ailleurs.
La page de connexion est disponible sur `/connexion/` ; après connexion, le formulaire de dépôt s’affiche à l’accueil.

## Comptes par défaut

Crée un compte local avec la commande ci-dessus ; aucun compte n'est préconfiguré dans une nouvelle base.

## Roadmap

- [x] Projet Django initialisé, gabarit commun des pages
- [x] Moteur : analyse audio, détection des notes, transposition, génération LilyPond (`partie_technique/`)
- [x] Cahier des charges
- [x] Connexion et déconnexion (les comptes sont créés via l'admin)
- [x] Dépôt d'un fichier audio et page de résultat de démonstration
- [x] Historique personnel des dépôts avec PDF de démonstration téléchargeable
- [ ] Inscription et choix de la tonalité
- [ ] Génération en tâche de fond (Celery) et intégration du moteur
- [ ] Suivi du traitement en temps réel (WebSocket)
- [ ] Transcription réelle et téléchargement du PDF généré
- [ ] Docker complet (PostgreSQL, Caddy, healthcheck, port 8080)
- [x] Pages d'erreur 404 et 500 personnalisées
- [x] Compte admin automatique en Docker (identifiants configurés dans `.env`)

## Modèle de données

Graphe des modèles à venir (généré avec `graph_models` de django-extensions) : `docs/models.png`.

## Documentation

- [Cahier des charges](cahier_des_charges_projet_python.md)
- [Cahier de labo](Cahier_de_labo.md) — le suivi au jour le jour est dans les issues GitHub
- [Guide de l'équipe](GUIDE_EQUIPE.md)
