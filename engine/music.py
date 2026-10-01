from .notes import position_note, note_vers_frequence, frequence_vers_note

"""Détection d'armure suivant le principe du projet initial (mode majeur)."""
NOMS = ['c', 'cis', 'd', 'dis', 'e', 'f', 'fis', 'g', 'gis', 'a', 'ais', 'b']
TONIQUES = {'c': 0, 'cis': 1, 'des': 1, 'd': 2, 'ees': 3, 'e': 4,
            'f': 5, 'fis': 6, 'ges': 6, 'g': 7, 'aes': 8, 'a': 9,
            'bes': 10, 'b': 11, 'ces': 11}
DIESES = ['c', 'g', 'd', 'a', 'e', 'b', 'fis', 'cis']
BEMOLS = ['c', 'f', 'bes', 'ees', 'aes', 'des', 'ges', 'ces']


def valider_tonalite(tonalite):
    if not isinstance(tonalite, str) or tonalite.lower().strip() not in TONIQUES:
        raise ValueError('Tonalité majeure attendue : ' + ', '.join(TONIQUES))
    return tonalite.lower().strip()


def determiner_tonalite(notes):
    compte = [0] * 12
    for note in notes:
        compte[position_note(note['nom']) % 12] += 1
    nombre = 0
    for alteree, naturelle in [(6, 5), (1, 0), (8, 7), (3, 2), (10, 9), (5, 4), (0, 11)]:
        if compte[alteree] <= compte[naturelle]:
            break
        nombre += 1
    if nombre:
        return DIESES[nombre]
    for alteree, naturelle in [(10, 11), (3, 4), (8, 9), (1, 2), (6, 7), (11, 0), (4, 5)]:
        if compte[alteree] <= compte[naturelle]:
            break
        nombre += 1
    return BEMOLS[nombre]


def intervalle_transposition(source, cible):
    return (TONIQUES[valider_tonalite(cible)] - TONIQUES[valider_tonalite(source)] + 6) % 12 - 6


def transposer(notes, source, cible):
    # Transposer revient à multiplier la fréquence par un rapport constant.
    rapport = 2 ** (intervalle_transposition(source, cible) / 12)
    resultat = []
    for note in notes:
        frequence = note_vers_frequence(note['nom'], note['octave']) * rapport
        nom, octave = frequence_vers_note(frequence)
        resultat.append({**note, 'nom_source': note['nom'], 'octave_source': note['octave'],
                         'nom': nom, 'octave': octave, 'frequence': frequence})
    return resultat


def nom_lilypond(nom_note, octave, tonalite):
    hauteur = position_note(nom_note)
    naturels = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}
    alterations = {lettre: 0 for lettre in naturels}
    bemol = tonalite in BEMOLS[1:]
    ordre = 'beadgcf' if bemol else 'fcgdaeb'
    nombre = BEMOLS.index(tonalite) if bemol else DIESES.index(tonalite)
    for lettre in ordre[:nombre]:
        alterations[lettre] = -1 if bemol else 1
    # Préférer l'orthographe de la gamme, y compris mi#, si# et dob.
    for lettre, naturel in naturels.items():
        alteration = alterations[lettre]
        if (naturel + alteration) % 12 == hauteur % 12:
            nom = lettre + ('is' if alteration == 1 else 'es' if alteration == -1 else '')
            octave += (hauteur - naturel - alteration) // 12
            break
    else:
        nom = (['c', 'des', 'd', 'ees', 'e', 'f', 'ges', 'g', 'aes', 'a', 'bes', 'b'] if bemol else NOMS)[hauteur % 12]
        octave += hauteur // 12
    return nom + "'" * max(0, octave - 3) + ',' * max(0, 3 - octave)
