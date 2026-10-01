# Guide de l'équipe — démarrer et travailler sur le projet

Ce guide explique comment installer le projet sur ton PC, comment on travaille avec Git, et où ranger tes fichiers. Le cahier des charges complet (répartition P1 / P2 / P3, contrats entre nous) est dans le [README](README.md).

---

## 1. Ce qui est déjà en place

| Élément | Où | Qui |
|---|---|---|
| Projet Django `partitionmusic` (Django 6.1, en français, fuseau `Europe/Paris`) | `partitionmusic/` | P1 |
| `.gitignore` (venv, `db.sqlite3`, `media/`, `__pycache__`) | racine | P1 |
| Dépendances | `requirements.txt` | P1 |
| App `comptes` (page de test sur `/comptes/`) | `comptes/` | P1 |
| **Gabarit commun `base.html`** (navbar, contenu, pied de page) | `templates/base.html` | P1 |
| **Style commun** | `static/css/style.css` | P1 |

---

## 2. Installer le projet chez toi (Windows)

### 2.1 Récupérer le code

```powershell
git checkout main
git pull
```

### 2.2 Créer ton environnement virtuel

Le venv est un dossier qui contient le Python et les bibliothèques **du projet uniquement**. Chacun crée le sien : il n'est **jamais** envoyé sur GitHub.

```powershell
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
```

✅ `(venv)` apparaît au début de la ligne du terminal. **Réactive-le à chaque nouveau terminal.**

### 2.3 Installer les dépendances et la base de données

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- `migrate` crée ta base locale `db.sqlite3` (elle reste sur ton PC, chacun a la sienne).
- `createsuperuser` crée ton compte admin pour `/admin/`.
- Ouvre http://127.0.0.1:8000/comptes/ : la page de test doit s'afficher avec la navbar.

### 2.4 Les pièges qu'on a déjà rencontrés

| Problème | Cause | Solution |
|---|---|---|
| `pip` n'est pas reconnu | la commande `python` pointe vers un autre Python (par exemple celui de MSYS2), sans pip | crée le venv avec `py -3.12 -m venv venv`, puis active-le |
| « l'exécution de scripts est désactivée » | PowerShell bloque `Activate.ps1` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, une seule fois |
| `pip.exe` manque dans `venv\Scripts` | la création du venv a été interrompue (`Ctrl+C`) | supprime `venv` et recrée-le, en **attendant** la fin (ça peut prendre une minute sans rien afficher) |
| `requirements.txt` illisible pour Git | dans Windows PowerShell, `>` écrit le fichier en UTF-16 | utilise `pip freeze \| Out-File -Encoding ascii requirements.txt` |

---

## 3. Travailler avec Git

```text
main          ●────────────●─────────────●───▶   version commune, toujours fonctionnelle
               \          ↑ PR          ↑ PR
ta branche      ●──●──●──┘   ●──●──●───┘           tu travailles ici
```

### Les règles

1. **On ne code jamais directement sur `main`.** Chacun a sa branche : `P1-comptes`, `P2-...`, `P3-...`.
2. **On commite souvent**, dès qu'une petite chose marche.
3. **On récupère régulièrement le travail des autres** : `git pull origin main`.
4. **On fusionne avec une Pull Request** sur GitHub, relue par un autre membre de l'équipe.
5. **Toujours faire `git status` avant `git add`**, pour vérifier ce qu'on envoie.

### Créer ta branche

```powershell
git checkout main
git pull
git checkout -b P2-partitions
git push -u origin P2-partitions
```

(Remplace `P2-partitions` par le nom de ta branche.)

### Le cycle de travail

```powershell
git status
git add .
git commit -m "Ce que j'ai fait"
git push
```

### Si tu installes une nouvelle bibliothèque

Mets à jour `requirements.txt` **et préviens l'équipe**, pour que chacun refasse `pip install -r requirements.txt` :

```powershell
pip install channels
pip freeze | Out-File -Encoding ascii requirements.txt
```

---

## 4. Créer ton app et ranger tes fichiers

### 4.1 Créer l'app

```powershell
python manage.py startapp partitions
```

### 4.2 La déclarer dans `partitionmusic/settings.py`

Ajoute **une ligne à la fin** de `INSTALLED_APPS`, **avec la virgule** (comme ça, la ligne suivante ajoutée par quelqu'un d'autre ne crée pas de conflit Git) :

```python
INSTALLED_APPS = [
    ...
    'comptes',
    'partitions',
]
```

### 4.3 Brancher tes URLs dans `partitionmusic/urls.py`

Crée `partitions/urls.py` (Django ne le crée pas), avec un `app_name`, puis ajoute **une seule ligne** dans le fichier du projet :

```python
path("", include("partitions.urls")),        # P2 : accueil et dépôt du son
path("dashboard/", include("dashboard.urls")),  # P3
```

Chacun gère ses routes dans **son** `urls.py`. Le fichier du projet ne contient qu'une ligne par app.

### 4.4 Où ranger quoi

```text
projet/
├── templates/
│   └── base.html                     ← COMMUN (P1), ne pas y mettre vos pages
├── static/
│   └── css/style.css                 ← COMMUN (P1)
│
└── partitions/                       ← TON app
    ├── templates/
    │   └── partitions/               ← oui, le nom de l'app deux fois
    │       └── home.html
    ├── static/
    │   └── partitions/
    │       └── js/uploader.js
    ├── urls.py
    └── views.py
```

**Pourquoi `partitions/templates/partitions/` ?** Django met tous les dossiers `templates/` dans un seul espace de recherche. Si deux apps ont un `home.html`, Django prend le premier trouvé et l'une des deux affiche la page de l'autre. Avec le sous-dossier, les noms deviennent `partitions/home.html` et `comptes/home.html` : plus de collision.

---

## 5. Utiliser `base.html`

Toutes les pages du site **héritent** de `templates/base.html`. Il fournit le `<head>`, la feuille de style, la navbar (avec connexion / inscription ou « Bonjour, nom ») et le pied de page. Toi, tu ne remplis que les **blocs**.

### Les blocs disponibles

| Bloc | Rôle | Valeur par défaut |
|---|---|---|
| `title` | texte de l'onglet | « Partition Musique » |
| `content` | contenu de la page | vide |

### Exemple de page

`partitions/templates/partitions/home.html` :

```django
{% extends "base.html" %}

{% block title %}Générer une partition{% endblock %}

{% block content %}
    <h1>Déposez votre audio</h1>
    <p>Bonjour {{ user.username }} !</p>
{% endblock %}
```

### Les règles

- `{% extends "base.html" %}` doit être **la toute première ligne**.
- **Tout ce qui est en dehors d'un bloc est ignoré.**
- Pas besoin de `<html>`, `<head>` ni `<body>` : ils viennent de `base.html`.
- La variable `{{ user }}` est disponible dans **tous** les templates, sans la passer depuis la vue.

### La vue correspondante

```python
from django.shortcuts import render


def home(request):
    return render(request, "partitions/home.html", {"titre": "..."})
```

- Le chemin du template part du dossier `templates/` : `"partitions/home.html"`.
- Le dictionnaire (le *contexte*) contient les variables utilisables dans le template avec `{{ titre }}`.
- ⚠️ Si une clé est mal orthographiée, Django n'affiche **pas d'erreur**, juste du vide.

### Ajouter du CSS ou du JS propre à ta page

Mets tes fichiers dans `ton_app/static/ton_app/`. Si tu as besoin d'un bloc supplémentaire dans `base.html` (par exemple pour charger tes scripts JS en bas de page), **demande à P1** plutôt que de modifier `base.html` toi-même : ça évite les conflits sur un fichier que tout le monde utilise.

---

## 6. Ce que P1 va fournir aux autres

| Quoi | Pour qui | Statut |
|---|---|---|
| `base.html` + `style.css` | P2, P3 | ✅ disponible |
| Pages connexion / déconnexion / inscription (`comptes:connexion`, `comptes:inscription`…) | tout le monde | à venir |
| `@login_required` redirige vers la page de connexion | P2, P3 | à venir |
| `comptes.notifications.notifier_utilisateur(user, titre, message, lien)` | P2 | à venir |
| WebSocket de notifications `/ws/notifications/` | P2, P3 | à venir |

En attendant les vraies pages de connexion, utilisez `/admin/` pour vous connecter avec votre superuser : la session est la même pour tout le site.

---

## 7. Commandes utiles

| Commande | Rôle |
|---|---|
| `venv\Scripts\Activate.ps1` | activer le venv |
| `python manage.py runserver` | lancer le site (`Ctrl+C` pour arrêter) |
| `python manage.py check` | vérifier le projet sans lancer le serveur |
| `python manage.py makemigrations` | préparer les changements de modèles |
| `python manage.py migrate` | appliquer les changements à la base |
| `python manage.py createsuperuser` | créer un compte admin |
| `python manage.py startapp nom` | créer une app |
| `git pull origin main` | récupérer le travail des autres |
