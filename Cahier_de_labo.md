# Cahier de labo

**Projet Python**

## 3e séance

### Ligne directrice

- Récupérer les notes avec la FFT. Associer aux fréquences le nom des notes avec la relation fréquence-note. Ne pas utiliser MIDI, tout faire manuellement
- Recomposer la partition avec LilyPond.
- Trouver les rythmes en repérant les temps forts ; autocorrélation.
- Transposition : vérifier que la tonalité est correcte, transposer d'une octave si nécessaire.

Le backend m’envoie le chemin du fichier et doit simplement appeler ma fonction `générer_partition()`.

Je dois renvoyer le chemin du PDF à Elyes (backend).

## 24/09

### Objectifs

- Revoir l’architecture.
- Définir toutes les pages, les fonctionnalités et la base de données.
- Se renseigner sur LilyPond.

### Ce qui a été fait

- Mise à jour de la répartition des tâches (pour que tout le monde touche à tout).
- Architecture mise à jour sur Git.

## 27/09

- Installation de LilyPond et compréhension du langage.
- Recherche d’une meilleure détection des notes et des rythmes. Les rythmes ne sont pas encore correctement détectés ; la détection des notes s’améliore, mais l’octave reste incorrecte.

## 28/09

- Poursuite du travail sur les rythmes (ajout du tempo pour aider à la reconstitution).
- Le problème d’octave des notes persiste.
- Besoin d’utiliser Celery, car la partie FFT prend du temps, donc faut la faire s'executer ailleurs.


## 08/10

Retour en arrière pour enlever quelques modif faites par l'IA car sinon on a 0.
Pas eu le temps de push car travaillé en local, pas dans le repo

## 15/10

Mettre ce que j'ai fait la semaine dernière dans le git
Maj les modif sur le git