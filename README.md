# Cahier des charges projet python — Application de génération et transposition de partitions musicales (Django)

## 1. Présentation du projet

### 1.1 Contexte

Le projet consiste à développer une application web **Django** permettant de transformer un fichier audio, ou un enregistrement réalisé directement depuis le navigateur, en une partition musicale.

L'utilisateur crée un compte, dépose ou enregistre un son, choisit une tonalité cible, et obtient une partition PDF automatiquement transposée. Il retrouve ensuite toutes ses partitions dans son espace personnel.

La génération pouvant prendre plusieurs secondes, elle est effectuée côté serveur, en tâche de fond. **La partie réseau du projet repose sur les WebSockets (Django Channels)** : progression du traitement en direct, notifications utilisateur, et tableau de bord administrateur en temps réel.

La priorité du projet est la **fiabilité de l'application, de l'interface et de la communication réseau**.

La précision de la reconnaissance musicale est secondaire : le moteur peut ne pas être fiable à 100 %, à condition que le reste de l'application fonctionne correctement.

---

# 2. Objectifs

L'application doit permettre à un utilisateur de :

1. créer un compte et se connecter ;
2. importer un fichier audio ou s'enregistrer au microphone ;
3. choisir la tonalité cible ;
4. lancer la génération de la partition ;
5. suivre la progression en direct, sans bloquer l'interface ;
6. être notifié lorsque le traitement est terminé, même depuis une autre page du site ;
7. visualiser et télécharger la partition ;
8. retrouver l'historique de ses partitions.

Et à un administrateur de :

1. suivre en temps réel les traitements en cours ;
2. consulter les statistiques du site ;
3. gérer les utilisateurs et les jobs.

L'application devra être simple à utiliser, visuellement agréable, responsive et résistante aux erreurs utilisateur.

---

# 3. Organisation de l'équipe

Le projet est découpé en **3 blocs fonctionnels**. Chaque personne développe son bloc **de A à Z** : modèles, vues, templates, JavaScript, WebSocket, tests.

| Personne   | Bloc                                     | Application Django        | Partie WebSocket                           |
| ---------- | ---------------------------------------- | ------------------------- | ------------------------------------------ |
| Personne 1 | Comptes utilisateurs & espace personnel  | `comptes/`                | Centre de notifications utilisateur        |
| Personne 2 | Dépôt du son, traitement & résultat      | `partitions/`             | Suivi du job et progression en direct      |
| Personne 3 | Moteur de partition & administration     | `engine/` + `dashboard/`  | Tableau de bord admin en temps réel        |

Chaque bloc a donc sa propre partie réseau. Les trois blocs communiquent via des **contrats d'interface** fixés dès le début (voir section 8).

---

# 4. Personne 1 — Comptes utilisateurs & espace personnel

### Responsabilité

Tout ce qui concerne l'utilisateur : son compte, sa session, son espace personnel et ses notifications.

### Pages

| URL                          | Page                                      |
| ---------------------------- | ----------------------------------------- |
| `/comptes/inscription/`      | Création de compte                        |
| `/comptes/connexion/`        | Connexion                                 |
| `/comptes/deconnexion/`      | Déconnexion                               |
| `/comptes/mot-de-passe/`     | Mot de passe oublié / réinitialisation    |
| `/comptes/profil/`           | Profil (nom, email, tonalité par défaut)  |
| `/comptes/mes-partitions/`   | Historique des partitions de l'utilisateur |

### Missions

* formulaire d'inscription avec validation (email unique, mot de passe robuste) ;
* connexion / déconnexion (système d'authentification Django) ;
* réinitialisation du mot de passe par email (backend console en développement) ;
* page de profil modifiable ;
* page « Mes partitions » : liste, recherche, téléchargement, suppression ;
* protection des pages (`@login_required`) et redirection vers la connexion ;
* template de base `base.html` : barre de navigation, pied de page, style global ;
* **centre de notifications** : icône cloche dans la navbar avec compteur de non-lues.

### Partie réseau — Notifications utilisateur

* WebSocket `WS /ws/notifications/` ouvert sur **toutes les pages** du site dès que l'utilisateur est connecté ;
* chaque utilisateur est abonné au groupe `user_{id}` ;
* à la réception d'un message : toast dans la page, compteur mis à jour, et notification système (Notification API du navigateur) ;
* les notifications sont aussi enregistrées en base (modèle `Notification`) pour être relues plus tard ;
* reconnexion automatique en cas de coupure.

Ainsi, l'utilisateur est prévenu que sa partition est prête même s'il est parti consulter son historique ou son profil.

### Modèles

```python
class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tonalite_defaut = models.CharField(max_length=10, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True)
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
```

### Livrables

```text
comptes/
├── models.py            # Profil, Notification
├── forms.py             # inscription, profil
├── views.py
├── urls.py
├── consumers.py         # NotificationConsumer
├── routing.py
├── notifications.py     # notifier_utilisateur(...)  ← utilisé par les autres
├── templates/comptes/
└── static/comptes/js/notifications.js

templates/base.html
static/css/style.css
```

---

# 5. Personne 2 — Dépôt du son, traitement & résultat

### Responsabilité

Le parcours principal : de la page d'accueil jusqu'à la partition téléchargée.

### Pages

| URL                          | Page                                             |
| ---------------------------- | ------------------------------------------------ |
| `/`                          | Accueil : présentation + dépôt / enregistrement  |
| `/jobs/{job_id}/`            | Écran de traitement puis de résultat             |

### Missions

**Dépôt du son**

* sélection d'un fichier `.wav` (bouton ou drag & drop) ;
* enregistrement au microphone (`MediaRecorder`) : durée, état, bouton stop ;
* lecteur audio pour réécouter ;
* supprimer / remplacer / recommencer ;
* choix de la tonalité cible (pré-remplie avec la tonalité par défaut du profil) ;
* bouton **Générer ma partition**.

**Traitement**

* modèle `Job` ;
* validation du fichier et de la tonalité (formulaire Django) ;
* sauvegarde du fichier dans `media/uploads/` ;
* création du job et lancement de la tâche **Celery** ;
* appel du moteur (fourni par la Personne 3) ;
* gestion des erreurs et du statut `FAILED`.

**Résultat**

* affichage du PDF dans la page ;
* bouton de téléchargement ;
* bouton « Générer une nouvelle partition ».

### Partie réseau — Suivi du job en direct

* WebSocket `WS /ws/jobs/{job_id}/`, groupe `job_{id}` ;
* le serveur envoie la **progression réelle** du traitement, étape par étape :

```json
{ "job_id": "8fd2...", "status": "PROCESSING", "progress": 45, "etape": "Détection des notes" }
```

* à la connexion, le consumer envoie immédiatement le statut courant (cas où le job finit avant l'ouverture du WebSocket) ;
* en cas de coupure : reconnexion automatique puis `GET /api/jobs/{id}/` pour récupérer le statut ;
* à la fin du job : appel de `notifier_utilisateur(...)` (Personne 1) et de `diffuser_evenement_admin(...)` (Personne 3).

```text
Génération de votre partition

████████████░░░░░░░  45 %

Détection des notes...
```

### Modèle

```python
class Job(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    progress = models.PositiveSmallIntegerField(default=0)
    audio = models.FileField(upload_to="uploads/")
    tonalite = models.CharField(max_length=10)
    resultat = models.FileField(upload_to="results/", blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    message_erreur = models.TextField(blank=True)
```

### API

| Méthode | URL                         | Rôle                               |
| ------- | --------------------------- | ---------------------------------- |
| POST    | `/api/jobs/`                | Upload audio + tonalité → job      |
| GET     | `/api/jobs/{id}/`           | Statut du job                      |
| GET     | `/api/jobs/{id}/result/`    | Téléchargement du PDF              |
| WS      | `/ws/jobs/{id}/`            | Progression et fin du traitement   |

Un utilisateur ne peut accéder qu'à **ses propres** jobs (sinon `404`).

### Livrables

```text
partitions/
├── models.py            # Job
├── forms.py
├── views.py             # pages + API JSON
├── urls.py
├── tasks.py             # tâche Celery process_job
├── consumers.py         # JobConsumer
├── routing.py
├── templates/partitions/
│   ├── home.html
│   └── job_detail.html
└── static/partitions/js/
    ├── uploader.js
    ├── recorder.js
    ├── api.js
    └── job_socket.js
```

---

# 6. Personne 3 — Moteur de partition & administration

### Responsabilité

Le cœur technique (transformer un son en partition) et la supervision du site.

## 6.1 Moteur de partition

Reprise du code Python existant, rendu utilisable par Django.

### Pipeline

```text
Audio → Lecture du signal → Découpage → FFT → Détection des fréquences
→ Filtrage → Fréquence → note → Notes / accords → Temps forts
→ Tonalité → Transposition → Code LilyPond → Compilation → PDF
```

### Missions

* isoler le traitement dans une fonction appelable ;
* recevoir le chemin du fichier audio et la tonalité cible ;
* écrire le PDF à l'emplacement demandé ;
* **signaler la progression** à chaque étape via un callback (pour la barre de progression en direct) ;
* lever des exceptions claires (`AudioInvalideError`, `LilypondError`...) ;
* tester le moteur sur plusieurs fichiers (tests unitaires) ;
* installer LilyPond dans l'image Docker.

### Interface fournie

```python
def generer_partition(fichier_audio, tonalite_cible, output, on_progress=None):
    """
    on_progress(pourcentage: int, etape: str) est appelé à chaque étape.
    Retourne le chemin du PDF. Lève une exception en cas d'échec.
    """
```

## 6.2 Page d'administration

Un tableau de bord personnalisé réservé aux comptes `staff`, en plus de l'admin Django standard (`/admin/`).

| URL                          | Page                                        |
| ---------------------------- | ------------------------------------------- |
| `/dashboard/`                | Vue d'ensemble + jobs en direct             |
| `/dashboard/jobs/`           | Liste des jobs (filtres, relancer, supprimer) |
| `/dashboard/utilisateurs/`   | Liste des utilisateurs (activer / désactiver) |

### Missions

* accès restreint (`@staff_member_required`) ;
* statistiques : nombre d'utilisateurs, de partitions, taux d'échec, temps moyen de traitement, tonalités les plus demandées ;
* liste des jobs avec filtres par statut, utilisateur et date ;
* relancer un job en échec, supprimer un job et ses fichiers ;
* consulter le message d'erreur d'un job ;
* activer / désactiver un compte utilisateur ;
* enregistrement des modèles dans l'admin Django.

### Partie réseau — Tableau de bord en temps réel

* WebSocket `WS /ws/admin/`, groupe `admin`, accessible uniquement aux comptes staff (vérification dans `connect()`) ;
* chaque création, progression, fin ou échec de job apparaît **instantanément** dans le tableau ;
* compteurs mis à jour en direct (jobs en cours, utilisateurs connectés) ;
* **utilisateurs connectés** : compteur alimenté par les connexions au WebSocket de notifications (Personne 1).

### Livrables

```text
engine/
├── audio.py
├── music.py
├── lilypond.py
├── parameters.py
├── engine.py
└── tests/

dashboard/
├── views.py
├── urls.py
├── consumers.py         # AdminConsumer
├── routing.py
├── events.py            # diffuser_evenement_admin(...)  ← utilisé par la Personne 2
├── templates/dashboard/
└── static/dashboard/js/dashboard.js
```

---

# 7. Architecture technique

```text
┌──────────────────────────────────────────────────────────────┐
│                         NAVIGATEUR                           │
│  Templates Django + JS                                       │
│                                                              │
│  Comptes (P1)      Dépôt / Résultat (P2)   Dashboard (P3)    │
│  WS notifications  WS job                  WS admin          │
└───────┬──────────────────┬──────────────────────┬────────────┘
        │        HTTP + WebSocket                 │
        ▼                  ▼                      ▼
┌──────────────────────────────────────────────────────────────┐
│               SERVEUR DJANGO (ASGI : Daphne + Channels)      │
│                                                              │
│  comptes/          partitions/            dashboard/         │
│  NotificationCons. JobConsumer            AdminConsumer      │
└───────────────────────────┬──────────────────────▲───────────┘
                            │ tâche                │ group_send
                            ▼                      │
                    ┌───────────────┐      ┌───────┴───────┐
                    │ Celery worker │─────▶│     Redis     │
                    └───────┬───────┘      │ broker +      │
                            │              │ channel layer │
                            ▼              └───────────────┘
                    ┌───────────────┐
                    │   engine/     │
                    │  + LilyPond   │
                    └───────┬───────┘
                            ▼
                       partition.pdf
```

### Flux réseau d'une génération

```text
1. POST /api/jobs/                         → Job PENDING
2. Navigateur ouvre WS /ws/jobs/{id}/
3. Celery démarre                          → PROCESSING
4. engine appelle on_progress(%)           → group_send job_{id}  + admin
5. Fin du traitement                       → COMPLETED / FAILED
                                           → group_send job_{id}  (page résultat)
                                           → group_send user_{id} (notification)
                                           → group_send admin     (dashboard)
```

---

# 8. Contrats d'interface entre les personnes

À fixer **dès la première séance** pour que chacun puisse avancer seul.

| Fourni par | Utilisé par | Contrat                                                                 |
| ---------- | ----------- | ----------------------------------------------------------------------- |
| P1         | P2, P3      | `templates/base.html` : tout le monde étend ce template                 |
| P1         | P2          | `comptes.notifications.notifier_utilisateur(user, titre, message, lien)` |
| P2         | P1, P3      | Modèle `partitions.Job` (champs de la section 5)                        |
| P3         | P2          | `engine.engine.generer_partition(fichier, tonalite, output, on_progress)` |
| P3         | P2          | `dashboard.events.diffuser_evenement_admin(job)`                        |

### Format des messages WebSocket

Tous les messages sont en JSON et ont un champ `type` :

```json
{ "type": "job.progress",  "job_id": "...", "progress": 45, "etape": "FFT" }
{ "type": "job.completed", "job_id": "...", "result": "/api/jobs/.../result/" }
{ "type": "job.failed",    "job_id": "...", "error": "Impossible de générer la partition" }
{ "type": "notification",  "titre": "Partition terminée", "message": "...", "lien": "/jobs/.../" }
{ "type": "admin.stats",   "jobs_en_cours": 3, "utilisateurs_connectes": 12 }
```

En attendant que le moteur soit prêt, la Personne 2 utilise une **fausse fonction** `generer_partition` qui attend quelques secondes et renvoie un PDF d'exemple.

---

# 9. Technologies

| Domaine            | Technologies                                                          |
| ------------------ | --------------------------------------------------------------------- |
| Frontend           | Templates Django, HTML, CSS (Tailwind ou Bootstrap), JavaScript natif |
| API navigateur     | `fetch`, `WebSocket`, `MediaRecorder`, `Notification`                 |
| Backend            | Django, Django Channels, Daphne                                       |
| Asynchrone         | Celery                                                                |
| Réseau / messages  | Redis (broker Celery + channel layer Channels)                        |
| Traitement musical | Python, NumPy, SciPy, FFT, LilyPond                                   |
| Base de données    | SQLite (prototype)                                                    |
| Déploiement        | Docker Compose : `web`, `worker`, `redis`                             |

---

# 10. Structure du projet

```text
projet-python-partition-musique/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env
│
├── partitionmusic/        # configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py            # routage HTTP + WebSocket
│   └── celery.py
│
├── templates/base.html    # P1
├── static/css/style.css   # P1
│
├── comptes/               # P1
├── partitions/            # P2
├── dashboard/             # P3
├── engine/                # P3
│
└── media/
    ├── uploads/
    └── results/
```

---

# 11. Gestion des erreurs

| Cas                                  | Responsable | Comportement attendu                              |
| ------------------------------------ | ----------- | ------------------------------------------------- |
| Identifiants incorrects              | P1          | Message clair, pas d'indication du champ fautif   |
| Email déjà utilisé                   | P1          | Message sur le formulaire                         |
| Page protégée sans être connecté     | P1          | Redirection vers la connexion                     |
| Aucun fichier / format non supporté  | P2          | Message avant l'envoi et côté serveur (`400`)     |
| Fichier trop volumineux              | P2          | Message clair (`400`)                             |
| Micro refusé                         | P2          | Message expliquant comment autoriser le micro     |
| Job d'un autre utilisateur           | P2          | `404`                                             |
| Perte du WebSocket                   | P1, P2, P3  | Reconnexion automatique + récupération de l'état  |
| Échec du moteur / de LilyPond        | P3 → P2     | Exception claire → job `FAILED` + message         |
| Accès au dashboard sans être staff   | P3          | `403` / redirection                               |

---

# 12. Lancement du projet (développement)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# terminal 1 : Redis
docker run -p 6379:6379 redis

# terminal 2 : serveur Django (Daphne via Channels)
python manage.py runserver

# terminal 3 : worker Celery
celery -A partitionmusic worker -l info
```

Ou avec Docker :

```bash
docker compose up
```

---

# 13. Perspectives d'évolution

## 13.1 Évolutions réseau (WebSocket)

* **Transcription en direct au micro** : l'audio est envoyé par morceaux via WebSocket pendant l'enregistrement, et les notes détectées s'affichent en temps réel sur une portée.
* **File d'attente en direct** : afficher « Vous êtes 3ᵉ dans la file » et le temps d'attente estimé, mis à jour en continu.
* **Partage d'une partition en temps réel** : un lien de partage ouvre une salle où plusieurs personnes voient la même partition ; changer la tonalité met à jour la partition chez tout le monde.
* **Édition collaborative** : corriger les notes détectées à plusieurs, chacun voyant les modifications des autres en direct (curseurs, présence).
* **Commentaires et chat** sur une partition, avec réception instantanée.
* **Mode répétition / jam** : un « chef » lance la lecture, le défilement de la partition est synchronisé sur tous les appareils connectés.
* **Notifications multi-appareils** : lancer la génération sur ordinateur, être notifié sur son téléphone (groupe `user_{id}` partagé entre les sessions).
* **Messages de l'administrateur** : annonce diffusée en direct à tous les utilisateurs connectés (maintenance, nouveauté).
* **Supervision avancée** : graphique en direct de la charge des workers Celery dans le dashboard.

## 13.2 Évolutions fonctionnelles

* formats audio supplémentaires : `.mp3`, `.m4a`, `.ogg` ;
* export **MIDI** et **MusicXML** (ouverture dans MuseScore) ;
* choix de l'instrument (clé de sol, clé de fa, tablature guitare) ;
* lecture de la partition générée dans le navigateur ;
* correction manuelle des notes avant génération du PDF ;
* partitions publiques et bibliothèque communautaire ;
* connexion avec Google / GitHub (OAuth) ;
* amélioration du moteur (détection du tempo, polyphonie, apprentissage automatique).

## 13.3 Évolutions techniques

* passage de SQLite à **PostgreSQL** ;
* stockage des fichiers sur un service objet (S3 / MinIO) ;
* plusieurs workers Celery pour traiter plus de jobs en parallèle ;
* limitation du nombre de générations par utilisateur ;
* suppression automatique des anciens fichiers ;
* **application mobile / PWA** avec notifications push ;
* API publique documentée pour des applications tierces ;
* intégration continue (tests automatiques à chaque push) et déploiement en ligne.
