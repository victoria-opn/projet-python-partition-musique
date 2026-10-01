"""Exemple modifiable : do majeur -> ré majeur, à 92 noires/minute.

Lancer : .venv/bin/python exemple_notes_manuelles.py
Les notes sont saisies directement, sans analyse audio ni estimation du tempo.
"""
from pathlib import Path
import json
import math

from .music import transposer
from .notes import note_vers_frequence
from .lilypond import generer_lilypond, ecrire_lilypond, compiler_lilypond

TONALITE_SOURCE = 'c'
TONALITE_CIBLE = 'd'
TEMPO_FINAL = 92
MESURE = (4, 4)

# Début d'« Au clair de la lune », proposé comme référence manuelle.
# Chaque ligne : (nom, octave, durée en noires).
# la4 = 440 Hz ; noire = 1, blanche = 2, ronde = 4,
# croche = 0.5, noire pointée = 1.5, double croche = 0.25.
# Un silence s'écrit ('silence', None, durée).
NOTES = [
    ('do', 4, 1), ('do', 4, 1), ('do', 4, 1), ('re', 4, 1),  # mesure 1
    ('mi', 4, 2), ('re', 4, 2),                               # mesure 2
    ('do', 4, 1), ('mi', 4, 1), ('re', 4, 2),                # mesure 3
    ('do', 4, 4),                                             # mesure 4
]


def convertir_notes(saisie):
    """Passer des noms français aux fréquences et positions en doubles croches."""
    demitons = {'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'sol': 7, 'la': 9, 'si': 11}
    notes = []
    position = 0
    for nom, octave, duree in saisie:
        if not math.isfinite(duree) or duree <= 0 or not float(duree * 4).is_integer():
            raise ValueError('Chaque durée doit être un multiple positif de 0.25 noire.')
        ticks = int(duree * 4)
        nom = nom.lower().replace('ré', 're')
        if nom != 'silence':
            alteration = 1 if nom.endswith('#') else -1 if nom.endswith('b') else 0
            naturel = nom[:-1] if alteration else nom
            if naturel not in demitons or not isinstance(octave, int):
                raise ValueError(f'Note invalide : {nom}, octave {octave}')
            frequence = note_vers_frequence(nom, octave)
            notes.append({'nom': nom, 'octave': octave, 'frequence': frequence,
                          'debut_tick': position, 'duree_ticks': ticks})
        position += ticks
    if not notes:
        raise ValueError('Saisir au moins une note.')
    # Le générateur complète automatiquement la dernière mesure par des silences.
    if position != notes[-1]['debut_tick'] + notes[-1]['duree_ticks']:
        raise ValueError('Terminer la saisie par une note ; la dernière mesure est complétée automatiquement.')
    return notes


def main():
    dossier = Path(__file__).resolve().parent / 'resultats' / 'notes_manuelles'
    dossier.mkdir(parents=True, exist_ok=True)
    source = convertir_notes(NOTES)
    cible = transposer(source, TONALITE_SOURCE, TONALITE_CIBLE)
    for nom, notes, tonalite in [('original_do', source, TONALITE_SOURCE),
                                  ('transpose_re', cible, TONALITE_CIBLE)]:
        code = generer_lilypond(notes, tonalite, TEMPO_FINAL, MESURE)
        chemin = dossier / (nom + '.ly')
        ecrire_lilypond(code, chemin)
        pdf = compiler_lilypond(chemin)
        print(f'PDF : {pdf}')
    (dossier / 'comparaison.json').write_text(json.dumps({
        'tonalite_source': TONALITE_SOURCE, 'tonalite_cible': TONALITE_CIBLE,
        'tempo_final': TEMPO_FINAL, 'notes_source': source, 'notes_transposees': cible,
    }, indent=2, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
