import numpy as np
import scipy.io.wavfile as wav



from parametres import (
    duree_decoupe,
    nombre_max_notes,
    decalage_octave_lilypond,
    seuil_amplitude_relatif,
    seuil_amplitude_globale,
    duree_mesure_max,
    duree_mesure_min,
    coeff_collage,
    seuil_alteration,
    tempo,
    tolerance_accord,
    temps_par_mesure,
    nom_fichier_audio,
    nom_fichier,
    notes_lilypond,
    notes_nom_reel,
    frequences_notes
)


def lire_audio(fichier):
    return wav.read(fichier)

def decouper_signal(signal, frequence):
    taille_bloc = int(frequence * duree_decoupe)
    longueur_valide = len(signal) - (len(signal) % taille_bloc)
    return signal[:longueur_valide].reshape(-1, taille_bloc)

def extraire_frequences(signal, frequence):
    # Transformée de Fourier
    tf = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), 1 / frequence)
    amplitudes = np.abs(tf)

    # Filtrage des fréquences audibles
    masque = (freqs > 20) & (freqs <= 20000)
    freqs = freqs[masque]
    amplitudes = amplitudes[masque]

    # Créer une liste de couples (fréquence, amplitude)
    couples = list(zip(freqs, amplitudes))

    # Supprimer les redondances : on ne garde qu'une seule fréquence si deux sont trop proches
    seuil_distance = 5  # Hz
    couples_uniques = []
    for freq, amp in sorted(couples, key=lambda x: x[1], reverse=True):
        if all(abs(freq - f) > seuil_distance for f, _ in couples_uniques):
            couples_uniques.append((freq, amp))

    # Appliquer un seuil sur l'amplitude basé sur un pourcentage de l'amplitude max
    if couples_uniques:
        amplitude_max = max(a for _, a in couples_uniques)
        seuil_amplitude = seuil_amplitude_relatif * amplitude_max
        couples_filtrés = [(f, a) for f, a in couples_uniques if a >= seuil_amplitude]
    else:
        couples_filtrés = []

    # Retourner les notes les plus fortes (jusqu'à la limite définie)
    return couples_filtrés[:nombre_max_notes]

def filtrer_amplitudes_globales(matrice_freqs):
    # Extraire toutes les amplitudes du morceau
    toutes_amplitudes = [amp for ligne in matrice_freqs for _, amp in ligne]
    if not toutes_amplitudes:
        return matrice_freqs

    # Définir un seuil global basé sur l'amplitude maximale du morceau
    amplitude_max_globale = max(toutes_amplitudes)
    seuil_global = seuil_amplitude_globale * amplitude_max_globale

    # Remplacer les amplitudes faibles par 0
    matrice_filtrée = []
    for ligne in matrice_freqs:
        ligne_filtrée = [(f, a if a >= seuil_global else 0.0) for f, a in ligne]
        matrice_filtrée.append(ligne_filtrée)

    return matrice_filtrée

def trouver_note(frequence):
    if frequence < 20 or frequence > 20000:
        return (-1, "rien")

    octave = 0
    while octave < len(frequences_notes) - 1 and frequences_notes[octave][0] < frequence:
        octave += 1
    octave -= 1

    for i in range(1, 12):
        if frequences_notes[octave][i] >= frequence:
            note_avant = frequences_notes[octave][i - 1]
            note_apres = frequences_notes[octave][i]
            index = i - 1 if (frequence - note_avant) < (note_apres - frequence) else i
            return (octave, notes_lilypond[index])

    note_fin = frequences_notes[octave][11]
    note_suivante = frequences_notes[octave + 1][0] if octave + 1 < len(frequences_notes) else None
    if note_suivante and (frequence - note_fin) < (note_suivante - frequence):
        return (octave, notes_lilypond[11])
    else:
        return (octave + 1, notes_lilypond[0]) if note_suivante else (octave, notes_lilypond[11])

def convertir_frequences_en_notes_avec_amplitude(matrice_freqs):
    """
    Transforme une matrice de (frequence, amplitude) en ((octave, note), amplitude)
    """
    resultat = []
    for ligne in matrice_freqs:
        ligne_notes = [((trouver_note(freq)), amp) for freq, amp in ligne if amp > 0.0]
        resultat.append(ligne_notes)
    return resultat

def enlever_doublons(liste_notes):
    resultat = []
    for accord in liste_notes:
        notes_presentes = []
        unique = []
        for note in accord:
            if note[0] not in notes_presentes:
                unique.append(note)
                notes_presentes.append(note[0])
            else:
                print("doublon detecte")
        resultat.append(unique)
    return resultat

def enlever_amplitude(liste_couple_notes):
    resultat = []
    for accord in liste_couple_notes:
        nouveau_accord = []
        if accord == []:
            resultat.append(nouveau_accord) # cas pour un silence
        else:
            for note in accord:
                nouveau_accord.append(note[0])
            resultat.append(nouveau_accord)
    return resultat
    
def coller_notes(liste_notes):
    info_notes_brutes = []
    notes_en_cours = {}

    for i, accord in enumerate(liste_notes):
        temps_actuel = i * duree_decoupe
        notes_actuelles = set()

        for (note, amplitude) in accord:
            notes_actuelles.add(note)

            if note in notes_en_cours:
                debut, amplitude_init = notes_en_cours[note]
                # Si amplitude diminue ou reste stable, continuer la note
                if amplitude <= coeff_collage * amplitude_init:
                    continue  # On ne modifie rien
                else:
                    # Nouvelle attaque plus forte : on finit l’ancienne note
                    info_notes_brutes.append((note, debut, temps_actuel, amplitude_init))
                    notes_en_cours[note] = (temps_actuel, amplitude)
            else:
                notes_en_cours[note] = (temps_actuel, amplitude)

        # Fin de notes absentes dans l'accord
        notes_finies = set(notes_en_cours.keys()) - notes_actuelles
        for note in notes_finies:
            debut, amp = notes_en_cours.pop(note)
            info_notes_brutes.append((note, debut, temps_actuel, amp))

    # Fin du morceau : ajouter notes restantes
    fin_total = len(liste_notes) * duree_decoupe
    for note, (debut, amp) in notes_en_cours.items():
        info_notes_brutes.append((note, debut, fin_total, amp))

    return info_notes_brutes

def convertir_en_noms_reels(tab_notes):
    resultat = []
    for accord in tab_notes:
        res = [notes_nom_reel[notes_lilypond.index(note)] for _, note in accord if note in notes_lilypond]
        resultat.append(res)
    return resultat

def temps_forts(info_notes_brutes):
    
    # On calcule la durée totale du morceau en prenant la plus grande valeur de fin de note
    temps_total = max(fin for _, _, fin, _ in info_notes_brutes)

    resolution = duree_decoupe
    nb_points = int(temps_total / resolution) + 1

    # On initialise un vecteur d'énergie (zéros) de taille correspondant au nombre de points temporels
    energie = np.zeros(nb_points)

    # Pour chaque note, on ajoute son amplitude à l'indice correspondant à son instant de début
    for _, debut, _, amplitude in info_notes_brutes:
        index = int(debut / resolution)
        if 0 <= index < nb_points:
            energie[index] += amplitude ** 2 # /!\  pas de POUSSIERE SOUS LE TAPIS

    # On applique une autocorrélation pour détecter la périodicité dans le signal d'énergie
    autocorr = np.correlate(energie, energie, mode='full')

    # On garde uniquement la deuxième moitié du signal d'autocorrélation car on a une symetrie de l'autocorrelation, donc on garde que le decalage positif
    autocorr = autocorr[autocorr.size // 2:]

    # On définit un décalage maximal pour la recherche du pic (lié à la durée max d'une mesure)
    max_lag = int(duree_mesure_max / resolution)

    # On cherche le décalage (lag) pour lequel l'autocorrélation est maximale (hors 0 car le decalage est de 0 et donc les 2 signaux sont les memes)
    pic_local = np.argmax(autocorr[1:max_lag]) + 1

    # On en déduit la période estimée des temps forts
    periode_estimee = pic_local * resolution

    # On génère la liste des temps théoriques des temps forts en suivant cette période
    temps_forts_list = []
    t = 0.0
    while t <= temps_total:
        temps_forts_list.append(t)
        t += periode_estimee

    # On va maintenant associer à chaque temps fort estimé la note la plus proche dans les données
    notes_temps_forts = []
    derniers_debuts = []

    for t_ref in temps_forts_list:
        # On cherche la note dont le début est le plus proche de ce temps fort
        note_proche = min(info_notes_brutes, key=lambda x: abs(x[1] - t_ref))
        debut_note = note_proche[1]

        # On ajoute cette note seulement si elle est suffisamment éloignée des précédentes
        if all(abs(debut_note - d) >= duree_mesure_min for d in derniers_debuts):
            notes_temps_forts.append(note_proche)
            derniers_debuts.append(debut_note)

    # On retourne la liste des notes considérées comme temps forts
    return notes_temps_forts