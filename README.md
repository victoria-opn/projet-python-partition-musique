# Cahier des charges projet python —  Application de génération et transposition de partitions musicales

## 1. Présentation du projet

### 1.1 Contexte

Le projet consiste à développer une application web permettant de transformer un fichier audio ou un enregistrement réalisé directement depuis le navigateur en une partition musicale.

L'utilisateur doit pouvoir choisir une tonalité cible afin que la partition générée soit automatiquement transposée.

La génération de la partition pouvant prendre plusieurs secondes, le traitement sera effectué côté serveur. L'utilisateur sera informé de la fin du traitement grâce à un système de notification utilisant une communication réseau entre le serveur et le navigateur.

La priorité du projet est la **fiabilité de l'application, de l'interface et du système de notification**.

La précision de la reconnaissance musicale est considérée comme secondaire : le moteur de génération de partition peut ne pas être fiable à 100 %, à condition que le reste de l'application fonctionne correctement.

---

# 2. Objectifs

L'application doit permettre à un utilisateur de :

1. importer un fichier audio ;
2. ou enregistrer directement un son depuis son microphone ;
3. choisir la transposition souhaitée ;
4. lancer la génération de la partition ;
5. continuer à utiliser l'interface pendant le traitement ;
6. être informé lorsque le traitement est terminé ;
7. visualiser le résultat ;
8. télécharger la partition générée.

L'application devra être :

* simple à utiliser ;
* visuellement agréable ;
* responsive ;
* résistante aux erreurs utilisateur ;
* capable de gérer un traitement relativement long sans bloquer l'interface ;
* capable d'informer l'utilisateur de la fin du traitement via le réseau.

---

# 3. Utilisateur cible

L'application est destinée à toute personne souhaitant obtenir rapidement une partition à partir d'un extrait musical.

Exemples :

* musicien ;
* étudiant en musique ;
* compositeur ;
* arrangeur ;
* utilisateur souhaitant transposer un morceau dans une autre tonalité.

Aucune connaissance technique ne doit être nécessaire pour utiliser l'application.

---

# 4. Parcours utilisateur

## Étape 1 — Arrivée sur l'application

L'utilisateur arrive sur une page principale présentant brièvement le service.

Il peut immédiatement choisir entre :

* **Importer un audio**
* **S'enregistrer**

---

## Étape 2 — Sélection ou enregistrement audio

### Option A — Import

L'utilisateur peut sélectionner un fichier audio depuis son ordinateur.

Formats acceptés dans la première version :

* `.wav`

Évolution possible :

* `.mp3`
* `.m4a`
* `.ogg`

Le fichier sélectionné est affiché dans l'interface.

L'utilisateur doit pouvoir :

* écouter le fichier ;
* supprimer le fichier ;
* sélectionner un autre fichier.

---

### Option B — Enregistrement microphone

L'utilisateur peut cliquer sur :

>  Commencer l'enregistrement

Le navigateur demande l'autorisation d'accéder au microphone.

Pendant l'enregistrement, l'application affiche :

* la durée ;
* l'état de l'enregistrement ;
* un bouton permettant de l'arrêter.

Une fois l'enregistrement terminé, l'utilisateur doit pouvoir :

* écouter son enregistrement ;
* recommencer ;
* conserver l'enregistrement.

---

# 5. Choix de la transposition

Avant de lancer le traitement, l'utilisateur choisit une tonalité cible.

La tonalité choisie est envoyée au backend avec le fichier audio.

Le backend transmet ensuite cette valeur au moteur de génération de partition.

---

# 6. Lancement de la génération

L'utilisateur clique sur :

> **Générer ma partition**

L'application transmet alors :

```text
Audio
+
Tonalité cible
        ↓
      API
        ↓
Création d'un traitement
```

Le serveur attribue au traitement un identifiant unique.

Exemple :

```text
job_id = 8fd20cd8-62e1-4aa3-b756...
```

Le traitement possède alors le statut :

```text
PENDING
```

puis :

```text
PROCESSING
```

---

# 7. Traitement audio

Le moteur de traitement reprend le code Python existant.

Le pipeline général est :

```text
Audio
  ↓
Lecture du signal
  ↓
Découpage du signal
  ↓
Transformée de Fourier
  ↓
Détection des fréquences
  ↓
Filtrage
  ↓
Conversion fréquence → note
  ↓
Détection des notes / accords
  ↓
Détection des temps forts
  ↓
Détermination de la tonalité
  ↓
Transposition
  ↓
Création du code LilyPond
  ↓
Compilation LilyPond
  ↓
Partition PDF
```

---

# 8. Gestion des traitements

Chaque génération sera considérée comme un **job**.

Un job possède au minimum :

```text
id
status
audio
tonalite
resultat
date_creation
message_erreur
```

Les statuts disponibles seront :

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

Exemple :

```json
{
  "id": "123456",
  "status": "PROCESSING",
  "tonalite": "g"
}
```

Lorsque la génération réussit :

```json
{
  "id": "123456",
  "status": "COMPLETED",
  "result": "/partitions/123456.pdf"
}
```

En cas d'erreur :

```json
{
  "id": "123456",
  "status": "FAILED",
  "error": "Impossible de générer la partition"
}
```

---

# 9. Notifications réseau

L'utilisateur ne doit pas avoir besoin de rafraîchir manuellement la page pour savoir si sa partition est terminée.

Une communication réseau persistante sera mise en place entre le frontend et le backend.

---

# 10. Notification navigateur

Lorsque le frontend reçoit l'événement réseau indiquant la fin du traitement, plusieurs notifications seront déclenchées.

### Notification dans l'application

Exemple :

> Votre partition est prête !

Un bouton apparaît :

> Voir la partition

---

### Notification système

Si l'utilisateur a autorisé les notifications navigateur :

> Partition terminée
> Votre partition transposée est prête.

La notification utilisera la **Notification API du navigateur**.

Ainsi, même si l'utilisateur consulte un autre onglet, il pourra être informé de la fin de la génération, sous réserve des permissions et restrictions du navigateur.

---

# 11. Gestion des erreurs réseau

Le système doit prendre en compte la perte temporaire de la connexion WebSocket.

Si la connexion est perdue :

```text
WebSocket disconnected
        ↓
tentative de reconnexion
        ↓
GET /jobs/{id}
        ↓
récupération du statut actuel
```

Cela permet d'éviter de perdre l'information si la partition est terminée pendant une coupure réseau.

---

# 12. API backend

Le backend exposera plusieurs routes.

## Upload et création d'un traitement

```http
POST /api/jobs
```

Données :

```text
audio
tonalite
```

Réponse :

```json
{
  "job_id": "123456",
  "status": "PENDING"
}
```

---

## Récupération d'un traitement

```http
GET /api/jobs/{job_id}
```

Exemple :

```json
{
  "job_id": "123456",
  "status": "PROCESSING"
}
```

---

## Récupération de la partition

```http
GET /api/jobs/{job_id}/result
```

Cette route retourne la partition PDF.

---

## WebSocket

```text
WS /ws/jobs/{job_id}
```

Le frontend se connecte au WebSocket associé au traitement.

Exemple de réponse :

```json
{
  "job_id": "123456",
  "status": "COMPLETED"
}
```

---

# 13. Architecture technique

L'architecture proposée est la suivante :

```text
┌─────────────────────────────┐
│          UTILISATEUR        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          FRONTEND           │
│                             │
│ React / HTML / CSS / JS     │
│                             │
│ - Upload                    │
│ - Microphone                │
│ - Sélection tonalité        │
│ - Affichage statut          │
│ - Affichage partition       │
│ - Notifications             │
└──────────────┬──────────────┘
               │
          HTTP / WebSocket
               │
               ▼
┌─────────────────────────────┐
│           BACKEND           │
│          FastAPI            │
│                             │
│ - API REST                  │
│ - Gestion fichiers          │
│ - Gestion jobs              │
│ - WebSocket                 │
│ - Gestion erreurs           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      MOTEUR DE PARTITION    │
│          Python             │
│                             │
│ - Analyse audio             │
│ - FFT                       │
│ - Détection notes           │
│ - Transposition             │
│ - Génération LilyPond       │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────────────┐
        │   LilyPond   │
        └──────┬───────┘
               │
               ▼
        partition.pdf
```

---

# 14. Technologies envisagées

## Frontend

* React
* Vite
* HTML
* CSS
* JavaScript ou TypeScript

Possibilité d'utiliser une bibliothèque CSS :

* Tailwind CSS

afin d'obtenir rapidement une interface moderne et responsive.

---

## Backend

* Python
* FastAPI
* WebSocket
* API REST

---

## Traitement musical

Les technologies déjà présentes dans le projet seront conservées :

* Python
* NumPy
* SciPy
* FFT
* LilyPond

---

## Stockage

Pour le prototype :

* fichiers sur le serveur ;
* SQLite pour conserver les informations des jobs.

Arborescence possible :

```text
data/
├── uploads/
│   ├── job-001.wav
│   └── job-002.wav
│
└── results/
    ├── job-001.pdf
    └── job-002.pdf
```

---


# 15. Écran de traitement, génération résultats

Une fois la génération lancée :

```text
Génération de votre partition

████████████░░░░░░░

Analyse de l'audio en cours...
```

---

# 16. Gestion des erreurs

Le frontend doit gérer différents scénarios.

---

# 17. Répartition des tâches

## Personne 1 — Moteur audio & génération de partition

### Responsabilité principale

Rendre le .py qui génére la partition utilisable par le backend

### Missions

* permettre au backend de transmettre le chemin du fichier audio ;
* permettre au backend de transmettre la tonalité cible ;
* modifier la gestion des fichiers ;
* isoler le traitement dans une fonction ;
* générer le fichier LilyPond ;
* compiler le fichier ;
* retourner le PDF généré ;
* gérer les exceptions du moteur ;
* tester le moteur sur plusieurs fichiers.

### Interface à fournir au backend

```python
generer_partition(
    fichier_audio,
    tonalite_cible,
    output
)
```

### Livrables

```text
engine/
├── audio.py
├── music.py
├── lilypond.py
├── parameters.py
└── engine.py
```

## Personne 2 — Frontend / UI / UX

### Responsabilité principale

Développer toute l'interface utilisateur.

### Missions

Créer :

* la page d'accueil ;
* le composant d'upload ;
* le drag & drop ;
* l'enregistrement microphone ;
* le lecteur audio ;
* le choix de la tonalité ;
* le bouton de génération ;
* l'écran de chargement ;
* l'écran de résultat ;
* les messages d'erreur ;
* les notifications visuelles ;
* l'intégration avec l'API ;
* la connexion WebSocket ;
* l'affichage du résultat.

### Pages / composants

```text
frontend/
├── components/
│   ├── AudioUploader
│   ├── AudioRecorder
│   ├── AudioPlayer
│   ├── KeySelector
│   ├── GenerateButton
│   ├── JobStatus
│   ├── Notification
│   └── ScoreViewer
│
├── pages/
│   ├── Home
│   ├── Processing
│   └── Result
│
└── services/
    ├── api
    └── websocket
```
---

## Personne 3 — Backend / réseau / notifications

### Responsabilité principale

Développer le serveur et faire communiquer toutes les parties de l'application.

Cette personne joue le rôle d'intégrateur entre :

```text
Frontend
↕
Backend
↕
Moteur musical
```

### Missions

Créer l'API FastAPI.

Routes principales :

```text
POST /api/jobs
GET /api/jobs/{id}
GET /api/jobs/{id}/result
WS /ws/jobs/{id}
```

Gérer :

* réception des fichiers ;
* sauvegarde des fichiers ;
* génération des identifiants ;
* création des jobs ;
* lancement du moteur ;
* traitement asynchrone ;
* récupération des résultats ;
* stockage des statuts ;
* erreurs ;
* WebSocket ;
* reconnexion ;
* transmission de la notification ;
* téléchargement du PDF.

### Exemple de traitement

```python
async def process_job(job_id):
    try:

        set_status(job_id, "PROCESSING")

        result = generer_partition(...)

        set_status(job_id, "COMPLETED")

        await notify_user(job_id)

    except Exception as e:

        set_status(job_id, "FAILED")

        await notify_user(job_id)
```


---

# 18. Répartition synthétique

| Domaine                 | Personne 1 | Personne 2 | Personne 3 |
| ----------------------- | :--------: | :--------: | :--------: |
| Analyse audio           |      ✅     |            |            |
| Détection notes         |      ✅     |            |            |
| Transposition           |      ✅     |            |            |
| LilyPond                |      ✅     |            |            |
| Génération PDF          |      ✅     |            |            |
| Design                  |            |      ✅     |            |
| Upload UI               |            |      ✅     |            |
| Microphone              |            |      ✅     |            |
| Responsive              |            |      ✅     |            |
| API                     |            |            |      ✅     |
| Upload serveur          |            |            |      ✅     |
| Jobs                    |            |            |      ✅     |
| Traitement asynchrone   |            |            |      ✅     |
| WebSocket               |            |            |      ✅     |
| Notifications réseau    |            |      ✅     |      ✅     |
| Gestion erreurs serveur |            |            |      ✅     |
| Intégration finale      |      ✅     |      ✅     |      ✅     |

---
