# Cahier des charges

## 1. Présentation de l'entreprise et du projet

Nous simulons entreprise spécialisée dans le développement de solutions numériques autour de la musique et du traitement audio.

L'entreprise souhaite proposer un service permettant de simplifier la transposition de partitions musicales à partir d'un fichier audio ou d'un enregistrement réalisé directement depuis une application web.

Le projet consiste donc à développer une application web capable de recevoir un audio, de l'analyser afin d'en extraire les notes principales, puis de générer une partition musicale transposée selon une tonalité choisie par l'utilisateur.

Le but est donc de créer un script Python permettant d'analyser un fichier audio, de détecter des notes, d'effectuer une transposition et de générer une partition. Ce script constituera la base technique du projet.

Le développement devra principalement permettre de transformer ce script en un service utilisable depuis une interface web fiable, simple et agréable à utiliser.

Le projet doit également intégrer une composante réseau importante : lorsque la génération de la partition est terminée, l'utilisateur doit être averti automatiquement par une notification.

---

## 2. Objectif du projet

L'objectif principal est de développer une application web permettant à un utilisateur de générer automatiquement une partition musicale à partir d'un fichier audio.

L'utilisateur devra pouvoir :

* Déposer un fichier audio sur l'application ;
* Sélectionner la tonalité dans laquelle il souhaite transposer le morceau ;
* Lancer la génération de la partition ;
* Etre informé de l'avancement du traitement ;
* Recevoir une notification lorsque la génération est terminée ;
* Consulter et télécharger la partition obtenue.

La qualité de la transcription musicale n'est pas le critère principal du projet. Le script de reconnaissance des notes pourra comporter certaines imprécisions.

En revanche, le fonctionnement général du site devra être particulièrement fiable.

---

## 3. Périmètre du projet

La répartition prévue est la suivante :

### Victoria Oppeneau — Traitement audio et génération de partition

Missions principales :

* permettre au backend de transmettre le fichier audio à analyser ;
* permettre au backend de transmettre la tonalité cible ;
* gérer la détection des notes ;
* gérer la transposition ;
* gérer la détection des rythmes ;
* reconstruire la partition ;
* compiler la partition ;
* retourner le fichier généré.

---

### Axel Clément — Frontend et interface utilisateur

Missions principales :

* créer la page d'accueil ;
* créer l'interface de dépôt d'un fichier audio ;
* mettre en place le drag and drop ;
* permettre l'enregistrement depuis le microphone ;
* permettre l'écoute de l'audio avant envoi ;
* créer le choix de la tonalité cible ;
* créer le bouton de lancement ;
* afficher l'état du traitement ;
* afficher les messages d'erreur ;
* afficher la notification lorsque la partition est prête ;
* afficher le résultat ;
* permettre le téléchargement de la partition une fois le ;
* rendre l'application responsive et agréable visuellement;
* conteneurisation compléte de l'application et déploiement sur un registre.

---

### Elyes Krimi — Backend, réseau et notifications

Missions principales :

* comptes utilisateurs : inscription, connexion, déconnexion ;
* contrôle d'accès : pages réservées aux utilisateurs connectés, chacun ne voit que ses propres traitements ;
* créer le backend Django : modèles, vues et routes utilisées par le frontend ;
* recevoir les fichiers audio envoyés depuis le frontend et vérifier leur format et leur taille ;
* stocker les fichiers audio et les partitions générées (médias) ;
* créer un identifiant unique pour chaque traitement ;
* lancer le moteur de génération en tâche de fond (Celery et Redis) pour ne jamais bloquer le serveur ;
* intégrer le moteur de Victoria : appel de sa fonction, gestion de ses erreurs ;
* gérer le statut de chaque génération (en attente, en cours, terminé, erreur) ;
* permettre au frontend de récupérer les résultats ;
* mettre en place les communications réseau : WebSocket avec Django Channels et Daphne ;
* transmettre au frontend l'avancement et la fin du traitement ;
* gérer les notifications et la reconnexion en cas de coupure réseau ;
* gérer les erreurs serveur, avec des pages d'erreur 404 et 500 personnalisées ;
* rendre l'administration Django utilisable pour tous les modèles, avec le compte `admin` / `projetinfo1A` créé automatiquement ;
* configurer la base de données PostgreSQL ;
* permettre le téléchargement des partitions ;
* mettre en place l'intégration continue (tests automatiques avec GitHub Actions).

---

### 3.2 Ressources techniques

#### Traitement audio

Le traitement audio s'appuiera principalement sur Python (NumPy, FFT) ;

#### Frontend
Templates Django, HTML, CSS et JavaScript : les pages sont générées par Django, sans framework frontend séparé ;

#### Backend
Python, Django 6.1 (pile recommandée par le cours), Django Channels et Daphne pour les WebSockets, Celery et Redis pour les traitements en tâche de fond, PostgreSQL pour la base de données.

#### Hébergement
Machine virtuelle personnelle : tous les services (site, base de données, stockage des fichiers) y tournent dans des conteneurs Docker, derrière le reverse proxy Caddy.


---

## 4. Délai

Date de fin du projet : 09/12 (soutenance)

| Personne | 10/09 | 16/09 | 23/09 | 01/10 | 08/10 | 15/10 | 04/11 | 05/11 | 25/11 | 26/11 | 27/11 | 02/12 | 04/12 | 09/12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Victoria | Recherche sur les méthodes de transcription audio vers notes et définition de l'architecture du moteur | Mise en place de la lecture d'un fichier audio et récupération du signal | Découpage du signal et mise en place de l'analyse fréquentielle avec FFT | Détection des fréquences dominantes et conversion en notes musicales | Amélioration de la détection des notes, filtrage du bruit | Détermination de la tonalité et développement de la fonction de transposition | Développement de la génération de partition au format LilyPond | Compilation LilyPond et génération d'un fichier PDF | Intégration du moteur avec le backend et tests sur plusieurs fichiers audio | Correction des erreurs, amélioration de la stabilité et gestion des cas limites | Travail sur le PowerPoint de soutenance | Tests de démonstration | Validation finale du moteur | Soutenance |
| Axel | Création des maquettes du site, choix du design et définition du parcours utilisateur | Création des templates Django et développement de la page d'accueil | Développement de l'import audio et du drag and drop | Ajout du lecteur audio et du sélecteur de tonalité | Développement de l'enregistrement audio depuis le microphone | Connexion du frontend au backend pour l'envoi de l'audio et de la tonalité | Création de l'écran de traitement et affichage des différents statuts | Connexion au WebSocket et mise en place des notifications visuelles | Développement de la page résultat avec affichage et téléchargement de la partition | Responsive design, amélioration graphique et gestion des erreurs utilisateur | Travail sur le PowerPoint de soutenance | Tests finaux frontend et corrections | Préparation de la démonstration | Soutenance |
| Elyes | Définition de l'architecture backend et des échanges entre frontend, backend et moteur | Choix de Django (pile recommandée par le cours) et prise en main avec le tutoriel officiel | Création du dépôt Git, du projet Django et du guide d'équipe | Création de l'application comptes et du gabarit commun des pages | Prise en compte des consignes du module (Docker, PostgreSQL, aucune IA pour le code) et réorganisation | Comptes : inscription, connexion, déconnexion, contrôle d'accès | Modèle des traitements, upload et stockage des fichiers, traitement asynchrone avec Celery | Mise en place du WebSocket (Channels) pour suivre l'état du traitement, notifications et reconnexion réseau | Intégration du backend avec le moteur audio de Victoria | Gestion des erreurs, pages 404/500, compte admin par défaut, intégration continue | Travail sur le PowerPoint de soutenance | Tests de bout en bout | Validation finale du backend | Soutenance |

## 5. MVP et paliers de livraison

Compte tenu du délai et de la date de soutenance (09/12), le projet est organisé autour d'un **MVP (Minimum Viable Product)**, présenté au minimum lors de la soutenance, puis de **paliers successifs** que l'équipe présentera selon le temps disponible. Comme indiqué en section 2, la fiabilité du fonctionnement général du site est prioritaire sur la qualité de la transcription musicale.

### 5.1 MVP (livrable minimum pour la soutenance)

Le MVP doit permettre de réaliser le parcours complet de bout en bout, de façon fiable :

* l'utilisateur crée un compte et se connecte ; il ne voit que ses propres traitements ;
* l'utilisateur dépose un fichier audio depuis une page web ;
* il sélectionne la tonalité cible ;
* il lance la génération de la partition ;
* le backend reçoit le fichier, crée un identifiant unique de traitement et lance le moteur ;
* le moteur détecte les notes (FFT), effectue la transposition et génère un PDF ;
* le statut du traitement est consultable (en cours, terminé, erreur) ;
* l'utilisateur peut consulter et télécharger la partition obtenue ;
* les erreurs principales sont signalées par un message clair (fichier invalide, erreur serveur), avec des pages d'erreur 404 et 500 personnalisées ;
* l'administration Django est utilisable pour tous les modèles, avec le compte `admin` / `projetinfo1A` créé automatiquement sur toute nouvelle base ;
* image Docker minimale de l'application ;

La transcription peut comporter des imprécisions, ce qui est acceptable pour le MVP (étant donné que plusieurs méthodes de calcul ont déjà été effectué et aucune solution exacte n'a pour l'instant été trouvé : La partition est pour l'instant correcte).

### 5.2 Palier 1 : communication réseau et confort d'utilisation

Si le MVP est validé dans les temps :

* mise en place des WebSockets pour suivre l'avancement en temps réel ;
* notification automatique lorsque la partition est prête ;
* drag and drop du fichier audio ;
* lecteur audio pour écouter le fichier avant envoi.
* publication de l'image sur un registre (GHCR) pour que chaque intervenant puisse l'exécuter sans problème de build ;

### 5.3 Palier 2 : fonctionnalités avancées

* enregistrement direct depuis le microphone ;
* détection des rythmes pour une partition plus fidèle ;
* gestion de la reconnexion réseau et des cas limites ;
* interface responsive et amélioration graphique.

### 5.4 Palier 3 : consolidation

* amélioration de la précision de la détection des notes (filtrage du bruit, stabilité) ;
* tests sur plusieurs navigateurs et plusieurs fichiers audio ;
* tests de bout en bout et corrections finales.

### 5.5 Récapitulatif

| Niveau | Contenu principal | Statut à la soutenance |
|---|---|---|
| MVP | Comptes et connexion, dépôt audio, choix de la tonalité, génération du PDF, statut, téléchargement, administration | Obligatoire |
| Palier 1 | WebSockets, notifications, drag and drop, lecteur audio | Si le temps le permet |
| Palier 2 | Microphone, rythmes, reconnexion réseau, responsive | Si le temps le permet |
| Palier 3 | Précision de la détection, tests multi-navigateurs, tests de bout en bout | Si le temps le permet |