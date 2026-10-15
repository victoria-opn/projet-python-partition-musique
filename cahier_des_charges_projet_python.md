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

* créer l'API backend ;
* recevoir les fichiers audio envoyés depuis le frontend ;
* stocker temporairement les fichiers ;
* créer un identifiant unique pour chaque traitement ;
* lancer le moteur de génération ;
* gérer le statut de chaque génération ;
* permettre au frontend de récupérer les résultats ;
* mettre en place les communications réseau ;
* mettre en place les WebSockets ;
* transmettre au frontend l'information lorsque le traitement est terminé ;
* gérer les notifications ;
* gérer les erreurs serveur ;
* permettre le téléchargement des partitions.

---

### 3.2 Ressources techniques

#### Traitement audio

Le traitement audio s'appuiera principalement sur Python (NumPy, FFT) ;

#### Frontend
HTML, CSS, React ;

#### Backend
Python, FastAPI, API REST, WebSocket


---

## 4. Budget prévisionnel

L'équipe projet est composée de :
* un développeur spécialisé dans le traitement audio et la génération de partitions ;
* un développeur frontend chargé de l'interface et de l'expérience utilisateur ;
* un développeur backend chargé de l'API, du réseau et du système de notification.

Pour cette simulation, le coût journalier moyen d'un développeur junior est estimé à **300 € par jour**.

Le projet est estimé à environ **10 jours de travail par personne**, soit :

| Ressource                     | Nombre de jours | Coût journalier |  Coût total |
| ----------------------------- | --------------: | --------------: | ----------: |
| Développeur traitement audio  |        10 jours |           300 € |     3 000 € |
| Développeur frontend          |        10 jours |           300 € |     3 000 € |
| Développeur backend / réseau  |        10 jours |           300 € |     3 000 € |
| **Total ressources humaines** |    **30 jours** |                 | **9 000 €** |

---

L'application nécessite un serveur permettant d'héberger le backend, de recevoir les fichiers audio, d'exécuter les traitements Python, de stocker temporairement les fichiers générés, de gérer les connexions WebSocket.


| Ressource                                 | Coût estimé |
| ----------------------------------------- | ----------: |
| Hébergement du frontend                   |        50 € |
| Hébergement du backend                    |       150 € |
| Stockage des fichiers audio et partitions |        50 € |
| Base de données                           |        50 € |
| **Total infrastructure**                  |   **300 €** |

---

Afin de simuler une mise en production réelle, un nom de domaine peut être acheté pour rendre l'application accessible avec une adresse dédiée.

Le certificat HTTPS pourra être obtenu gratuitement via les solutions proposées par l'hébergeur.

| Ressource        | Coût estimé |
| ---------------- | ----------: |
| Nom de domaine   |        20 € |
| Certificat HTTPS |         0 € |
| **Total**        |    **20 €** |

---

Une partie du budget est réservée aux phases de tests, de correction des anomalies et de mise en production.

Cette phase comprend notamment les tests fonctionnels, les tests de communication réseau, les tests du système de notification, les tests sur plusieurs navigateurs, les tests de l'enregistrement microphone, la correction des bugs, la configuration finale du serveur.

Une enveloppe de **600 €** est prévue pour cette phase.

---

Une marge d'environ **10 %** est ajoutée afin d'anticiper d'éventuels coûts supplémentaires. Cette marge est estimée à environ **1 000 €**.

---

| Bilan budgétaire              |      Montant |
| ----------------------------- | -----------: |
| Ressources humaines           |      9 000 € |
| Infrastructure et hébergement |        300 € |
| Nom de domaine et sécurité    |         20 € |
| Logiciels et licences         |          0 € |
| Tests et mise en production   |        600 € |
| Marge pour imprévus           |      1 000 € |
| **TOTAL PRÉVISIONNEL**        | **10 920 €** |

L'enveloppe budgétaire globale du projet est donc estimée à environ :

# **11 000 €**

---

## 5. Délai

Date de fin du projet : 09/12 (soutenance)

| Personne | 10/09 | 16/09 | 23/09 | 01/10 | 08/10 | 15/10 | 04/11 | 05/11 | 25/11 | 26/11 | 27/11 | 02/12 | 04/12 | 09/12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Victoria | Recherche sur les méthodes de transcription audio vers notes et définition de l'architecture du moteur | Mise en place de la lecture d'un fichier audio et récupération du signal | Découpage du signal et mise en place de l'analyse fréquentielle avec FFT | Détection des fréquences dominantes et conversion en notes musicales | Amélioration de la détection des notes, filtrage du bruit | Détermination de la tonalité et développement de la fonction de transposition | Développement de la génération de partition au format LilyPond | Compilation LilyPond et génération d'un fichier PDF | Intégration du moteur avec le backend et tests sur plusieurs fichiers audio | Correction des erreurs, amélioration de la stabilité et gestion des cas limites | Travail sur le PowerPoint de soutenance | Tests de démonstration | Validation finale du moteur | Soutenance |
| Axel | Création des maquettes du site, choix du design et définition du parcours utilisateur | Création du projet frontend et développement de la page d'accueil | Développement de l'import audio et du drag and drop | Ajout du lecteur audio et du sélecteur de tonalité | Développement de l'enregistrement audio depuis le microphone | Connexion du frontend au backend pour l'envoi de l'audio et de la tonalité | Création de l'écran de traitement et affichage des différents statuts | Connexion au WebSocket et mise en place des notifications visuelles | Développement de la page résultat avec affichage et téléchargement de la partition | Responsive design, amélioration graphique et gestion des erreurs utilisateur | Travail sur le PowerPoint de soutenance | Tests finaux frontend et corrections | Préparation de la démonstration | Soutenance |
| Elyes | Définition de l'architecture backend et des échanges entre frontend, backend et moteur | Création du projet FastAPI et des premières routes API | Développement de la route d'upload des fichiers audio et gestion du stockage | Mise en place du système de jobs avec identifiant unique et statuts | Développement du traitement asynchrone pour éviter de bloquer le serveur | Création des routes permettant de consulter le statut et récupérer le résultat | Mise en place du WebSocket pour suivre l'état du traitement | Développement du système de notification et gestion de la reconnexion réseau | Intégration du backend avec le moteur audio | Tests complets de l'API, gestion des erreurs réseau et stabilisation | Travail sur le PowerPoint de soutenance | Tests de bout en bout | Validation finale du backend | Soutenance |

## 6. MVP et paliers de livraison

Compte tenu du délai et de la date de soutenance (09/12), le projet est organisé autour d'un **MVP (Minimum Viable Product)**, présenté au minimum lors de la soutenance, puis de **paliers successifs** que l'équipe présentera selon le temps disponible. Comme indiqué en section 2, la fiabilité du fonctionnement général du site est prioritaire sur la qualité de la transcription musicale.

### 6.1 MVP (livrable minimum pour la soutenance)

Le MVP doit permettre de réaliser le parcours complet de bout en bout, de façon fiable :

* l'utilisateur dépose un fichier audio depuis une page web ;
* il sélectionne la tonalité cible ;
* il lance la génération de la partition ;
* le backend reçoit le fichier, crée un identifiant unique de traitement et lance le moteur ;
* le moteur détecte les notes (FFT), effectue la transposition et génère un PDF ;
* le statut du traitement est consultable (en cours, terminé, erreur) ;
* l'utilisateur peut consulter et télécharger la partition obtenue ;
* les erreurs principales sont signalées par un message clair (fichier invalide, erreur serveur).
* image Docker minimale de l'application ;

La transcription peut comporter des imprécisions, ce qui est acceptable pour le MVP (étant donné que plusieurs méthodes de calcul ont déjà été effectué et aucune solution exacte n'a pour l'instant été trouvé : La partition est pour l'instant correcte).

### 6.2 Palier 1 : communication réseau et confort d'utilisation

Si le MVP est validé dans les temps :

* mise en place des WebSockets pour suivre l'avancement en temps réel ;
* notification automatique lorsque la partition est prête ;
* drag and drop du fichier audio ;
* lecteur audio pour écouter le fichier avant envoi.
* publication de l'image sur un registre (GHCR) pour que chaque intervenant puisse l'exécuter sans problème de build ;

### 6.3 Palier 2 : fonctionnalités avancées

* enregistrement direct depuis le microphone ;
* détection des rythmes pour une partition plus fidèle ;
* gestion de la reconnexion réseau et des cas limites ;
* interface responsive et amélioration graphique.

### 6.4 Palier 3 : consolidation

* amélioration de la précision de la détection des notes (filtrage du bruit, stabilité) ;
* tests sur plusieurs navigateurs et plusieurs fichiers audio ;
* tests de bout en bout et corrections finales.

### 6.6 Récapitulatif

| Niveau | Contenu principal | Statut à la soutenance |
|---|---|---|
| MVP | Dépôt audio, choix de la tonalité, génération du PDF, statut, téléchargement | Obligatoire |
| Palier 1 | WebSockets, notifications, drag and drop, lecteur audio | Si le temps le permet |
| Palier 2 | Microphone, rythmes, reconnexion réseau, responsive | Si le temps le permet |
| Palier 3 | Précision de la détection, tests multi-navigateurs, tests de bout en bout | Si le temps le permet |