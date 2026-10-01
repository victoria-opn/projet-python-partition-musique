"""Relation entre fréquences, noms français et octaves, sans numéros MIDI."""
import math

NOMS = ['do', 'do#', 're', 're#', 'mi', 'fa', 'fa#', 'sol', 'sol#', 'la', 'la#', 'si']
NATURELLES = {'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'sol': 7, 'la': 9, 'si': 11}


def position_note(nom):
    nom = nom.lower().replace('ré', 're')
    alteration = 1 if nom.endswith('#') else -1 if nom.endswith('b') else 0
    naturel = nom[:-1] if alteration else nom
    if naturel not in NATURELLES:
        raise ValueError(f'Nom de note invalide : {nom}')
    return NATURELLES[naturel] + alteration


def note_vers_frequence(nom, octave):
    """La4 = 440 Hz ; un demi-ton multiplie la fréquence par 2**(1/12)."""
    if not isinstance(octave, int) or not -1 <= octave <= 10:
        raise ValueError('Octave entière attendue entre -1 et 10.')
    return 440 * 2 ** ((position_note(nom) - 9) / 12 + octave - 4)


TABLE_FREQUENCES = [(nom, octave, note_vers_frequence(nom, octave))
                    for octave in range(-1, 11) for nom in NOMS]


def frequence_vers_note(frequence):
    """Chercher la note tempérée la plus proche dans la table de fréquences."""
    if not math.isfinite(frequence) or frequence <= 0:
        raise ValueError('La fréquence doit être positive et finie.')
    nom, octave, _ = min(TABLE_FREQUENCES,
                         key=lambda note: abs(math.log2(frequence / note[2])))
    return nom, octave
