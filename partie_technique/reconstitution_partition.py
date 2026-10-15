import subprocess

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


note_to_demiton = {
    "c": 0, "cis": 1, "des": 1,
    "d": 2, "dis": 3, "ees": 3,
    "e": 4, "f": 5, "fis": 6, "ges": 6,
    "g": 7, "gis": 8, "aes": 8,
    "a": 9, "ais": 10, "bes": 10,
    "b": 11, "h": 11
}

demiton_to_note_diese = {
    0: "c", 1: "cis", 2: "d", 3: "dis", 4: "e", 5: "f",
    6: "fis", 7: "g", 8: "gis", 9: "a", 10: "ais", 11: "b"
}

demiton_to_note_bemol = {
    0: "c", 1: "des", 2: "d", 3: "ees", 4: "e", 5: "f",
    6: "ges", 7: "g", 8: "aes", 9: "a", 10: "bes", 11: "b"
}


bemols_equivalents_dieses = {
    "cis": "des",  # do♯ = ré♭
    "dis": "ees",  # ré♯ = mi♭
    "eis": "f",    # mi♯ = fa
    "fis": "ges",  # fa♯ = sol♭
    "gis": "aes",  # sol♯ = la♭
    "ais": "bes",  # la♯ = si♭
    "bis": "c",    # si♯ = do
}



def transformer_en_bemols(info_notes_b):
    notes_converties = []
    
    for (octave, nom_note), debut, fin, amplitude in info_notes_b:
        if nom_note in bemols_equivalents_dieses:
            nom_note = bemols_equivalents_dieses[nom_note]
        notes_converties.append(((octave, nom_note), debut, fin, amplitude))
    
    return notes_converties


# Calculer le dictionnaire contenant les occurences de chaque note
def nombre_notes(info_notes_brutes):
    compteur = {note: 0 for note in notes_lilypond}
    
    for note_info in info_notes_brutes:
        _, nom_note = note_info[0]  # (octave, nom_note)
        if nom_note in compteur:
            compteur[nom_note] += 1
    
    return compteur

# Renvoie la liste des bemols ou dieses (regarder le premier element pour savoir) 
def TrouverAlterations(info_notes_brutes):
    ordre_dieses = ["fis", "cis", "gis", "dis", "ais", "f", "s"]
    ordre_bemols = ["ais", "dis", "gis", "cis", "fis", "b", "e"]
    alteration = []
    
    dico_occurences = nombre_notes(info_notes_brutes)
    
    # dieses
    for note in ordre_dieses:
        
        index = notes_lilypond.index(note)

        note_inf = notes_lilypond[index - 1]
        
        # Nombre d’occurrences des deux notes
        occur_note = dico_occurences.get(note, 0)
        occur_inf = dico_occurences.get(note_inf, 0)

        if occur_note > occur_inf:
            alteration.append(note)
        else:
            break  # dès qu’une condition échoue, on s’arrête
            
    # bemols
    if alteration == []:
        for note in ordre_bemols:
            if note == "b":     # cas pour le do
                if dico_occurences.get("b", 0) <= dico_occurences.get("c", 0):
                    alteration.append("b")
                else:
                    break
                
            else:
                index = notes_lilypond.index(note)
        
                note_sup = notes_lilypond[index + 1]
                
                # Nombre d’occurrences des deux notes
                occur_note = dico_occurences.get(note, 0)
                occur_sup = dico_occurences.get(note_sup, 0)
        
                if occur_note > occur_sup:
                    alteration.append(note)
                else:
                    break  # dès qu’une condition échoue, on s’arrête
            
    return alteration


def determiner_tonalite(alterations):

    tonalites_majeures_diese = ["c", "g", "d", "a", "e", "b", "fis", "cis"]
    tonalites_majeures_bemol = ["c", "f", "bes", "ees", "aes", "des", "ges", "ces"]

    if len(alterations) == 0:
        return "c"
    else:
        if alterations[0] == "fis":  # cas ou on a des dieses
            return tonalites_majeures_diese[len(alterations)]
        else:
            return tonalites_majeures_bemol[len(alterations)]



def decouper_en_mesures(notes, temps_forts):
    # Récupère les débuts des mesures depuis les temps forts
    debuts_mesures = sorted([note[1] for note in temps_forts]) 

    # Ajoute une mesure initiale si des notes commencent avant le premier temps fort
    if notes and notes[0][1] < debuts_mesures[0]:
        debuts_mesures = [0.0] + debuts_mesures

    # Calculer les fins de mesure (la dernière mesure va jusqu'à la fin de la dernière note)
    fins_mesures = debuts_mesures[1:] + [max(note[2] for note in notes)]

    mesures = []

    for debut, fin in zip(debuts_mesures, fins_mesures):
        mesure_notes = [note for note in notes if debut <= note[1] < fin]
        mesures.append(mesure_notes)

    # Calculer la durée moyenne d'une mesure
    durees = [fin - debut for debut, fin in zip(debuts_mesures, fins_mesures)]
    duree_moyenne = sum(durees) / len(durees)

    return mesures, duree_moyenne


def regrouper_notes_accords0(mesure):
    if not mesure:
        return []

    # Trie les notes par temps de début
    mesure_ordonnee = sorted(mesure, key=lambda note: note[1])
    groupes = []
    groupe_actuel = [mesure_ordonnee[0]]

    for note in mesure_ordonnee[1:]:
        dernier_debut = groupe_actuel[0][1]
        if abs(note[1] - dernier_debut) <= tolerance_accord:
            groupe_actuel.append(note)
        else:
            groupes.append(groupe_actuel)
            groupe_actuel = [note]

    groupes.append(groupe_actuel)
    return groupes


#Retourne une liste d'accords : chaque accord est une paire (liste_de_notes, durée).
def regrouper_notes_accords(mesure):
    
    # Extraire tous les points de changement (début ou fin de note)
    points = set()
    for note in mesure:
        points.add(note[1])  # début
        points.add(note[2])  # fin
    instants = sorted(points)

    accords = []
    for i in range(len(instants) - 1):
        debut = instants[i]
        fin = instants[i + 1]

        # Trouver les notes qui sont actives dans cet intervalle
        notes_dans_accord = [note for note in mesure if note[1] < fin and note[2] > debut]

        if notes_dans_accord:
            accords.append((notes_dans_accord, debut, fin))

    return accords


def regrouper_accord(info_note_mesures):
    resultat = []
    for mesure in info_note_mesures:
        resultat.append(regrouper_notes_accords(mesure))
    return resultat

    
def convertir_duree_en_valeur_rythmique(duree, duree_mesure):
    """Arrondi les durées"""
    
    if duree_mesure <= 0:
        raise ValueError("La durée d'une mesure doit être positive.")

    rapport = duree / duree_mesure
    valeurs = {
        "1": 1.0,
        "2": 0.5,
        "4": 0.25,
        "8": 0.125,
        "16": 0.0625,
    }

    return min(valeurs, key=lambda valeur: abs(rapport - valeurs[valeur]))
    
    
def lilypond_accord(accord, duree_ly):
    if len(accord[0]) == 1: # cas d'une note simple
        octave, nom = accord[0][0][0]
        octave_lilypond = octave_to_lilypond(octave)
        return f"{nom}{octave_lilypond}{duree_ly}"
    elif len(accord[0]) == 0: # cas pour un soupir
        return f"r{duree_ly}"
    else:
        notes_lilypond = []
        for note in accord[0]:
            octave, nom = note[0]
            octave_lilypond = octave_to_lilypond(octave)
            notes_lilypond.append(f"{nom}{octave_lilypond}")
        
        notes_str = ' '.join(notes_lilypond)
        return f"<{notes_str}>{duree_ly}"
    
    
# Convertit l'octave et le nom d'une note en syntaxe LilyPond
def octave_to_lilypond(octave):
    if octave == decalage_octave_lilypond:
        suffixe = ""
    elif octave > decalage_octave_lilypond:
        suffixe = "'" * (octave - decalage_octave_lilypond)
    else:
        suffixe = "," * (decalage_octave_lilypond - octave)
    return suffixe

#----------- Transposition

# def transposer_note(note, tonalite_source, tonalite_cible):
#     if note not in note_to_demiton:
#         return note

#     demiton_note = note_to_demiton[note]
#     demiton_source = note_to_demiton.get(tonalite_source, 0)
#     demiton_cible = note_to_demiton.get(tonalite_cible, 0)
    
#     decalage = (demiton_cible - demiton_source) % 12
#     demiton_transpose = (demiton_note + decalage) % 12

#     # Choix entre dièses et bémols selon la tonalité cible
#     prefer_bemol = tonalite_cible in ["f", "bes", "ees", "aes", "des", "ges", "ces"]
    
#     # Ne pas perdre l'information d’altération : garder le plus proche enharmonique
#     if prefer_bemol:
#         return demiton_to_note_bemol[demiton_transpose]
#     else:
#         return demiton_to_note_diese[demiton_transpose]


# def transposer_partition(info_notes_brutes, tonalite_source, tonalite_cible):
    
#     notes_transposees = []
    
#     for (octave, nom), debut, fin, amplitude in info_notes_brutes:
#         note_t = transposer_note(nom, tonalite_source, tonalite_cible)
#         notes_transposees.append(((octave, note_t), debut, fin, amplitude))
        
#     return notes_transposees
    
import re

def transposer_note(note, tonalite_source, tonalite_cible):
    def transposer_simple_note(n):
        if n not in note_to_demiton:
            return n
        demiton_note = note_to_demiton[n]
        demiton_source = note_to_demiton.get(tonalite_source, 0)
        demiton_cible = note_to_demiton.get(tonalite_cible, 0)
        decalage = (demiton_cible - demiton_source) % 12
        demiton_transpose = (demiton_note + decalage) % 12

        prefer_bemol = tonalite_cible in ["f", "bes", "ees", "aes", "des", "ges", "ces"]
        return (
            demiton_to_note_bemol[demiton_transpose]
            if prefer_bemol
            else demiton_to_note_diese[demiton_transpose]
        )

    # Détection d'un accord <...>
    if note.startswith("<") and note.endswith(">"):
        contenu = note[1:-1].strip()
        notes = contenu.split()
        transposed_notes = [transposer_simple_note(n) for n in notes]
        return "<" + " ".join(transposed_notes) + ">"
    else:
        return transposer_simple_note(note)

def transposer_partition(info_notes_brutes, tonalite_source, tonalite_cible):
    notes_transposees = []
    
    for (octave, nom), debut, fin, amplitude in info_notes_brutes:
        note_t = transposer_note(nom, tonalite_source, tonalite_cible)
        notes_transposees.append(((octave, note_t), debut, fin, amplitude))
        
    return notes_transposees


#----------- Lilypond
    
def generer_lilypond(notes_mesures_accords, duree_mesure, cle, tonalite, temps_par_mesure, ref_rythme):
    """
    Génère le code Lilypond correspondant aux accords de chaque mesure, en ajoutant des silences si nécessaire,
    y compris au début de la première mesure si elle commence en retard (levée/anacrouse).
    """

    # Tri des mesures par début
    notes_mesures_accords = sorted(
        notes_mesures_accords,
        key=lambda mesure: mesure[0][1] if mesure else float('inf')
    )
 
 
    # Tri des accords dans chaque mesure par leur début
    for i in range(len(notes_mesures_accords)):
        notes_mesures_accords[i] = sorted(notes_mesures_accords[i], key=lambda accord: accord[1])

    lignes = [
        "\\version \"2.24.2\"",
        "\\score {",
        "  \\new Staff {",
        f"    \\clef {cle}",
        f"    \\key {tonalite} \\major", 
        f"    \\time {temps_par_mesure}/{ref_rythme}",
        "    {"
    ]

    for idx, mesure in enumerate(notes_mesures_accords):
        mesure_ligne = []

        if not mesure:
            lignes.append("      r1 |")  # mesure vide : 1 ronde par défaut
            continue

        temps_courant = mesure[0][1]

        # Cas spécial : première mesure
        if idx == 0:
            if temps_courant > 0:
                # Silence avant la première note si la première mesure commence en retard
                duree_silence = temps_courant
                valeur_silence = convertir_duree_en_valeur_rythmique(duree_silence, duree_mesure)
                mesure_ligne.append(f"r{valeur_silence}")
        else:
            temps_courant = mesure[0][1]

        for accord in mesure:
            debut = accord[1]
            fin = accord[2]

            # Ajouter silence si trou entre temps_courant et début de l'accord
            if debut > temps_courant:
                duree_silence = debut - temps_courant
                valeur_silence = convertir_duree_en_valeur_rythmique(duree_silence, duree_mesure)
                mesure_ligne.append(f"r{valeur_silence}")

            duree = fin - debut
            valeur = convertir_duree_en_valeur_rythmique(duree, duree_mesure)
            code_lilypond = lilypond_accord(accord, valeur)
            mesure_ligne.append(code_lilypond)

            temps_courant = max(temps_courant, fin)

        lignes.append("      " + " ".join(mesure_ligne) + " \\bar \"!\"")

    lignes.append("    }")
    lignes.append("  }")
    lignes.append("}")

    return "\n".join(lignes)






def ecrire_lilypond(code_lilypond):
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(code_lilypond)


def compiler_lilypond():
    subprocess.run(["lilypond", nom_fichier])