"""Analyse monophonique : WAV -> notes nommées et datées, sans accords."""
import math

import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, find_peaks
from .notes import frequence_vers_note


def lire_audio(chemin):
    frequence, signal = wavfile.read(chemin)
    if signal.size == 0:
        raise ValueError("Le fichier WAV est vide.")
    # Convertir avant la moyenne évite les débordements des entiers PCM.
    if signal.dtype == np.uint8:
        signal = (signal.astype(float) - 128) / 128
    elif np.issubdtype(signal.dtype, np.integer):
        signal = signal.astype(float) / max(abs(np.iinfo(signal.dtype).min), np.iinfo(signal.dtype).max)
    else:
        signal = signal.astype(float)
    if not np.all(np.isfinite(signal)):
        raise ValueError("Le WAV contient des échantillons non finis.")
    if signal.ndim == 2:
        # Choisir le canal le plus énergétique évite l'annulation de canaux opposés.
        signal = signal[:, np.argmax(np.mean(signal ** 2, axis=0))]
    signal -= np.mean(signal)
    diviseur = math.gcd(frequence, 16000)
    signal = resample_poly(signal, 16000 // diviseur, frequence // diviseur)
    return 16000, signal


def frequence_fondamentale(bloc, frequence, fmin=130., fmax=2100.):
    """FFT fenêtrée : comparer les pics et leur famille d'harmoniques.

    Une seule fondamentale est retenue. On exige un pic à sa fréquence,
    pour ne pas inventer systématiquement une octave inférieure.
    """
    bloc = (bloc - np.mean(bloc)) * np.hanning(len(bloc))
    taille_fft = 2 ** int(np.ceil(np.log2(len(bloc) * 4)))
    spectre = np.abs(np.fft.rfft(bloc, n=taille_fft))
    frequences = np.fft.rfftfreq(taille_fft, 1 / frequence)
    if spectre.max() <= 1e-12:
        return None
    pics, _ = find_peaks(spectre, height=spectre.max() * .05)
    candidats = [p for p in pics if fmin <= frequences[p] <= fmax]
    if not candidats:
        return None
    meilleur = None
    score_max = -1
    resolution = frequence / taille_fft
    for pic in candidats:
        # Interpolation parabolique du pic : réduire l'erreur entre cases FFT.
        gauche, centre, droite = np.log(np.maximum(spectre[pic-1:pic+2], 1e-15))
        correction = .5 * (gauche - droite) / (gauche - 2 * centre + droite)
        fondamentale = (pic + correction) * resolution
        if not fmin <= fondamentale <= fmax:
            continue
        score = spectre[pic]
        for harmonique in range(2, 7):
            cible = fondamentale * harmonique
            tolerance = max(resolution * 2, cible * .012)
            proches = pics[np.abs(frequences[pics] - cible) <= tolerance]
            if len(proches):
                score += float(np.max(spectre[proches]))
        if score > score_max:
            score_max, meilleur = score, float(fondamentale)
    return meilleur


def analyser_audio(chemin, fmin=130., fmax=2100., seuil_silence=0.025):
    """Retourne des dictionnaires nom/octave/fréquence/début/fin (secondes), sans chevauchement.

    La plage par défaut va approximativement de do3 à do7 (la4 = 440 Hz).
    Les fenêtres de 60 ms se déplacent de 10 ms.
    """
    if not 40 <= fmin < fmax <= 4000:
        raise ValueError("Il faut 40 <= fmin < fmax <= 4000 Hz.")
    frequence, signal = lire_audio(chemin)
    pas = int(0.01 * frequence)
    demi = max(int(0.03 * frequence), int(2 * frequence / fmin))
    centres = np.arange(0, len(signal), pas)
    etendu = np.pad(signal, (demi, demi))
    # L'énergie utilise une fenêtre courte pour mieux placer attaques et silences.
    energies = np.array([np.sqrt(np.mean(etendu[c + demi - pas // 2:c + demi + pas // 2] ** 2)) for c in centres])
    seuil = max(1e-6, float(np.max(energies)) * seuil_silence)
    hauteurs = []
    frequences_detectees = []
    for centre, energie in zip(centres, energies):
        freq = frequence_fondamentale(etendu[centre:centre + 2 * demi], frequence, fmin, fmax) if energie > seuil else None
        frequences_detectees.append(freq)
        hauteurs.append(frequence_vers_note(freq) if freq else None)
    # Supprimer seulement les valeurs isolées entre deux hauteurs identiques.
    brutes = hauteurs.copy()
    for i in range(1, len(hauteurs) - 1):
        if brutes[i-1] == brutes[i+1]:
            hauteurs[i] = brutes[i-1]
    # Une brève excursion entre deux mêmes notes peut venir du vibrato.
    limites = [0] + [i for i in range(1, len(hauteurs))
                     if hauteurs[i] != hauteurs[i-1]] + [len(hauteurs)]
    for j in range(1, len(limites) - 2):
        a, b = limites[j:j+2]
        avant, pendant, apres = hauteurs[a-1], hauteurs[a], hauteurs[b]
        if avant is not None and pendant is not None and avant == apres:
            if (b-a) * pas / frequence <= .12:
                hauteurs[a:b] = [avant] * (b-a)
    # Une hausse nette après un creux marque une nouvelle attaque de même hauteur.
    attaques = set()
    derniere = -100
    for i in range(2, len(energies)):
        if energies[i] > seuil * 3 and energies[i] > 2.5 * max(energies[i-1], seuil) and i - derniere >= 8:
            attaques.add(i)
            derniere = i
    notes = []
    debut = 0
    for i in range(1, len(hauteurs) + 1):
        if i == len(hauteurs) or hauteurs[i] != hauteurs[debut] or i in attaques:
            fin = min(i * pas / frequence, len(signal) / frequence)
            if hauteurs[debut] is not None and fin - debut * pas / frequence >= 0.05:
                nom, octave = hauteurs[debut]
                valeurs = [f for f in frequences_detectees[debut:i]
                           if f is not None and frequence_vers_note(f) == (nom, octave)]
                if valeurs:
                    notes.append({"nom": nom, "octave": octave,
                                  "frequence_detectee": float(np.median(valeurs)),
                                  "debut": debut * pas / frequence, "fin": fin})
            debut = i
    if not notes:
        raise ValueError("Aucune note détectée : vérifier le signal et la plage fmin/fmax.")
    return notes


def quantifier_notes(notes, tempo=120, conserver_silence_initial=False):
    """Aligner la grille sur la première attaque, puis arrondir à la double croche.

    Le tempo doit correspondre à l'enregistrement. Les secondes originales sont
    conservées. Les coupures plus courtes qu'un tiers de tick sont considérées
    comme une articulation, sans supprimer les attaques de notes répétées.
    """
    if not math.isfinite(tempo) or tempo <= 0:
        raise ValueError("Le tempo doit être un nombre positif (noires par minute).")
    unite = 60 / tempo / 4
    origine = notes[0]['debut'] if notes and not conserver_silence_initial else 0
    resultat = []
    precedent = 0
    for i, note in enumerate(notes):
        fin_audio = note['fin']
        if i + 1 < len(notes):
            ecart = notes[i + 1]['debut'] - fin_audio
            if 0 <= ecart < unite / 3:
                fin_audio = notes[i + 1]['debut']
        debut = max(precedent, int(np.floor((note["debut"] - origine) / unite + 0.5)))
        fin = max(debut + 1, int(np.floor((fin_audio - origine) / unite + 0.5)))
        resultat.append({**note, "debut_tick": debut, "duree_ticks": fin - debut})
        precedent = fin
    return resultat


def estimer_tempo(notes):
    """Chercher une grille rythmique simple entre 40 et 200 noires/minute.

    On compare les durées et les écarts entre attaques aux valeurs usuelles.
    Une légère préférence pour les noires limite les choix à tempo double.
    Ce choix reste ambigu sans information sur la partition originale.
    """
    if not notes:
        raise ValueError('Impossible d’estimer le tempo sans notes.')
    durees = [n['fin'] - n['debut'] for n in notes]
    intervalles = [b['debut'] - a['debut'] for a, b in zip(notes, notes[1:])]
    observations = np.array(durees)
    observations = observations[observations >= .08]
    if not len(observations):
        raise ValueError('Notes trop courtes pour estimer le tempo ; fournir tempo_source.')
    valeurs = np.array([1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64])
    meilleur = (float('inf'), 120.)
    for candidat in np.arange(40., 200.1, .1):
        ticks = observations * candidat / 15
        distances = np.abs(np.log2(ticks[:, None] / valeurs))
        indices = np.argmin(distances, axis=1)
        erreurs = distances[np.arange(len(ticks)), indices]
        # Limiter l'influence des mauvaises détections et des longues pauses.
        score = np.mean(np.minimum(erreurs, .5) ** 2)
        score += .001 * np.mean(np.abs(np.log2(valeurs[indices] / 4)))
        if intervalles:
            # Entre attaques, une note et un silence peuvent totaliser 5 ou 7
            # ticks : ne pas forcer cet intervalle à une durée de note usuelle.
            ecarts = np.array(intervalles) * candidat / 15
            proches = np.maximum(1, np.rint(ecarts))
            score += .2 * np.mean(np.minimum(np.abs(np.log2(ecarts / proches)), .5) ** 2)
        if score < meilleur[0]:
            meilleur = (score, candidat)
    return round(float(meilleur[1]), 1)
