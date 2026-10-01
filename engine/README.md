# Travail P3 : moteur et administration

Le code TIPE de Victoria est intégré dans `engine/`, sans modifier le dossier
original. Les modules correspondent au découpage du README :

- `audio.py` : lecture WAV, FFT, notes, rythme et estimation du tempo ;
- `music.py` et `notes.py` : tonalité, transposition, hauteurs ;
- `lilypond.py` : écriture et compilation PDF ;
- `parameters.py` : paramètres musicaux ;
- `interface_backend.py` : pipeline TIPE avec progression ;
- `engine.py` : contrat public P3 et exceptions ;
- `tests/` : tests musicaux et contrat d’intégration.

```python
from engine.engine import generer_partition

pdf = generer_partition(
    "melodie.wav", "d", "sortie/partition.pdf",
    on_progress=lambda pourcentage, etape: print(pourcentage, etape),
)
```

Le contrat accepte les quatre arguments du README. Un paramètre optionnel
`tempo=120` conserve la possibilité de choisir le tempo final du code TIPE.
La tonalité source et le tempo source sont estimés. Le moteur est destiné aux
mélodies monophoniques en mode majeur. Les callbacks signalent les étapes
réelles du pipeline ; ils ne simulent pas une progression pendant la FFT.
Chaque appel utilise un dossier temporaire distinct et écrit le PDF à l’endroit
demandé. Les erreurs audio/paramètres lèvent `AudioInvalideError` et les erreurs
de compilation lèvent `LilypondError`. LilyPond doit être dans le PATH.

## Lancer le projet

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir `/admin/login/`, puis `/dashboard/`. L’accueil `/` n’est pas fourni :
il appartient à P2. Le dashboard fonctionne sans `partitions/` et indique
que les jobs attendent l’intégration P2. La liste des utilisateurs et leur
activation/désactivation sont disponibles dès maintenant.

Redis est nécessaire pour la diffusion et la présence :

```bash
docker run --rm -p 6379:6379 redis:7-alpine
```

Ou utiliser `docker compose up --build` : l’image contient LilyPond et Compose
lance uniquement web et Redis. Le worker Celery sera ajouté par P2.
Créer le compte avec `docker compose exec web python manage.py createsuperuser`.
`REDIS_URL` et `ALLOWED_HOSTS` peuvent être configurés par variables d’environnement.
Les nouvelles dépendances doivent être signalées à l’équipe dans la PR.

## Contrats avec P1 et P2

P2 doit fournir son modèle `partitions.Job` et sa tâche
`partitions.tasks.process_job`. P3 ne crée pas ce modèle, les uploads,
les écrans de résultat ni le worker Celery.
Dès que l’app P2 est installée, le dashboard utilise le modèle existant pour
les statistiques, les filtres, les relances et les suppressions. Il enregistre
Job dans l’admin Django si P2 ne l’a pas déjà fait. Seuls les jobs en échec
peuvent être relancés ; la suppression des jobs en attente ou en cours est
refusée pour éviter une collision avec le worker.

P2 appelle le contrat `dashboard.events.diffuser_evenement_admin(job)` à la
création, progression, fin et échec. Les messages sont `admin.job` et
`admin.stats`, dans le groupe `admin`. Le WebSocket `/ws/admin/` exige une
session staff active. Le client reconnecte et récupère un instantané HTTP,
avec les statistiques et les 30 derniers jobs.

P1 appelle `dashboard.presence.connection_utilisateur(user_id, channel_name)`
à la connexion du WebSocket de notifications et toutes les 60 secondes
(heartbeat), puis `deconnexion_utilisateur(user_id, channel_name)` à la
fermeture. Ces fonctions diffusent les compteurs administrateur.
Redis compte les utilisateurs distincts, même s’ils ont plusieurs onglets,
et élimine les connexions sans heartbeat après 120 secondes.
Sans ce raccordement P1, le compteur ne reflète pas les sessions utilisateur.
Si Redis est absent, le compteur affiche « Indisponible ».

Chaque personne devra ajouter ses routes WebSocket au routeur ASGI commun
lors de son intégration. Le template `base.html`, le CSS commun et l’app
`comptes` sont inchangés, conformément au guide d’équipe.

## Vérification

```bash
python manage.py check
python manage.py test engine dashboard
python manage.py makemigrations --check --dry-run
```

Les tests couvrent la transcription réelle de WAV synthétiques, les notes
manuelles, le contrat moteur, les accès staff HTTP/WebSocket, l’activation des
comptes et le fonctionnement sans P2. La génération réelle d’un PDF LilyPond
est aussi vérifiée lors de l’intégration. Les actions sur les jobs attendent
le modèle et la tâche réels de P2 pour une vérification complète entre apps.
La pile Docker/Redis et le navigateur n’ont pas été lancés pour cette vérification.

Les ajouts P2 précédents sont retirés. Une sauvegarde de ces fichiers est
conservée hors du projet dans `/tmp/partition-musique-ajouts-p2`.
La table locale P2 a été supprimée après vérification qu’elle était vide,
avec une sauvegarde de SQLite dans ce même dossier. La branche de travail
est `P3-moteur-dashboard` ; la fusion dans `main` passe par une Pull Request
relue par un autre membre de l’équipe.
