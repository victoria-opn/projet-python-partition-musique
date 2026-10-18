# Partition Musique

Transcrire un morceau à l'oreille puis le transposer prend du temps : cette application web Django transforme un fichier audio en partition PDF transposée dans la tonalité choisie, avec un suivi du traitement en temps réel.

Le détail du projet (besoin, fonctionnalités, répartition des tâches, planning, MVP et paliers) est dans le [cahier des charges](cahier_des_charges_projet_python.md).

## Lancer le projet

```bash
git clone https://github.com/victoria-opn/projet-python-partition-musique.git
cd projet-python-partition-musique
docker compose up -d
```

Le site répond sur http://localhost:8080.

> La conteneurisation est en cours : en attendant, le projet se lance en local (voir ci-dessous).

### En local (développement)

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Comptes par défaut

`admin` / `projetinfo1A` (créé automatiquement sur toute nouvelle base — en cours).

## Roadmap

- [x] Projet Django initialisé, gabarit commun des pages
- [x] Moteur : analyse audio, détection des notes, transposition, génération LilyPond (`partie_technique/`)
- [x] Cahier des charges
- [ ] Comptes : inscription, connexion, déconnexion
- [ ] Dépôt d'un fichier audio et choix de la tonalité
- [ ] Génération en tâche de fond (Celery) et intégration du moteur
- [ ] Suivi du traitement en temps réel (WebSocket)
- [ ] Page de résultat et téléchargement du PDF
- [ ] Docker complet (PostgreSQL, Caddy, healthcheck, port 8080)
- [ ] Pages d'erreur 404 et 500, compte admin automatique
- [ ] Intégration continue (GitHub Actions)

## Modèle de données

Graphe des modèles à venir (généré avec `graph_models` de django-extensions) : `docs/models.png`.

## Documentation

- [Cahier des charges](cahier_des_charges_projet_python.md)
- [Cahier de labo](Cahier_de_labo.md) — le suivi au jour le jour est dans les issues GitHub
- [Guide de l'équipe](GUIDE_EQUIPE.md)
