"""Écriture de la partition monophonique et compilation LilyPond facultative."""
from pathlib import Path
import shutil
import subprocess

from .music import nom_lilypond, valider_tonalite

# Durées en doubles croches : rondes, blanches, noires, etc., pointées incluses.
DUREES = [(24, '1.'), (16, '1'), (12, '2.'), (8, '2'), (6, '4.'), (4, '4'), (3, '8.'), (2, '8'), (1, '16')]


def generer_lilypond(notes, tonalite, tempo=120, mesure=(4, 4)):
    tonalite = valider_tonalite(tonalite)
    numerateur, denominateur = mesure
    if not isinstance(numerateur, int) or numerateur <= 0 or denominateur not in (2, 4, 8, 16):
        raise ValueError('Mesure attendue : numérateur positif et dénominateur 2, 4, 8 ou 16.')
    longueur_mesure = numerateur * 16 // denominateur
    morceaux = []
    position = 0

    def ajouter(nom, duree):
        nonlocal position
        while duree > 0:
            disponible = min(duree, longueur_mesure - position % longueur_mesure)
            taille, valeur = next((n, v) for n, v in DUREES if n <= disponible)
            duree -= taille
            morceaux.append(nom + valeur + ('~' if duree and nom != 'r' else ''))
            position += taille
            if position % longueur_mesure == 0:
                morceaux.append('|')

    for note in notes:
        if note['debut_tick'] < position:
            raise ValueError('Les notes doivent être ordonnées et ne pas se chevaucher.')
        ajouter('r', note['debut_tick'] - position)
        ajouter(nom_lilypond(note['nom'], note['octave'], tonalite), note['duree_ticks'])
    if position % longueur_mesure:
        ajouter('r', longueur_mesure - position % longueur_mesure)
    musique = ' '.join(morceaux)
    return '\n'.join([
        '\\version "2.24.2"', '\\language "nederlands"', '\\score {', '  \\new Staff {',
        '    \\clef treble', f'    \\key {tonalite} \\major',
        f'    \\time {numerateur}/{denominateur}', f'    \\tempo 4 = {round(tempo)}',
        '    ' + musique, '    \\bar "|."', '  }', '  \\layout { }', '}', ''])


def ecrire_lilypond(code, chemin):
    Path(chemin).write_text(code, encoding='utf-8')
    return str(chemin)


def compiler_lilypond(chemin):
    if shutil.which('lilypond') is None:
        raise RuntimeError('LilyPond est absent du PATH. Installer LilyPond ou utiliser --sans-pdf.')
    chemin = Path(chemin).resolve()
    resultat = subprocess.run(['lilypond', '-o', str(chemin.with_suffix('')), str(chemin)], capture_output=True, text=True, timeout=120)
    if resultat.returncode != 0:
        raise RuntimeError('Erreur LilyPond :\n' + resultat.stderr)
    pdf = chemin.with_suffix('.pdf')
    if not pdf.exists():
        raise RuntimeError('LilyPond n’a pas produit le PDF attendu.')
    return str(pdf)
