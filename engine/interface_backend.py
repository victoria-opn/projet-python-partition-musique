"""Point d'entrée indépendant du site : résultat sérialisable en JSON."""
from pathlib import Path
import math

from .music import determiner_tonalite, transposer, valider_tonalite, intervalle_transposition
from .audio import analyser_audio, quantifier_notes, estimer_tempo
from .lilypond import generer_lilypond, ecrire_lilypond, compiler_lilypond
from .parameters import temps_par_mesure, ref_rythme


def generer_partition(chemin_audio, tonalite_cible, tempo, dossier_sortie='resultats',
                      *, mesure=(temps_par_mesure, ref_rythme),
                      compiler_pdf=True, tonalite_source=None, fmin=130., fmax=2100.,
                      conserver_silence_initial=False, tempo_source=None, on_progress=None):
    """Analyser un WAV, écrire le .ly et éventuellement le PDF.

    Le chemin du WAV déposé, la tonalité cible et le tempo sont obligatoires.
    Le tempo est celui de la partition finale, en noires par minute.
    Le tempo du WAV est estimé sauf si tempo_source est fourni.

    Les secondes décrivent l'audio ; les ticks décrivent la partition quantifiée
    (4 ticks par noire). Le backend pourra intercepter ValueError/OSError/RuntimeError.
    Utiliser un dossier_sortie distinct par requête dans un futur serveur.
    """
    def progress(value, label):
        if on_progress:
            on_progress(value, label)
    progress(5, "Lecture du fichier audio")
    chemin = Path(chemin_audio)
    if not chemin.is_file():
        raise FileNotFoundError(f'Fichier audio introuvable : {chemin}')
    cible = valider_tonalite(tonalite_cible)
    if isinstance(tempo, bool) or not isinstance(tempo, (int, float)) or not math.isfinite(tempo) or tempo <= 0:
        raise ValueError('Le tempo doit être un nombre positif (noires par minute).')
    if tempo_source is not None and (isinstance(tempo_source, bool) or not isinstance(tempo_source, (int, float)) or not math.isfinite(tempo_source) or tempo_source <= 0):
        raise ValueError('Le tempo source doit être un nombre positif.')
    source = valider_tonalite(tonalite_source) if tonalite_source is not None else None
    progress(15, "Détection des notes")
    notes = analyser_audio(chemin, fmin=fmin, fmax=fmax)
    progress(50, "Détection de la tonalité")
    source = source or determiner_tonalite(notes)
    tempo_audio = estimer_tempo(notes) if tempo_source is None else tempo_source
    origine = 0 if conserver_silence_initial else notes[0]["debut"]
    progress(65, "Transposition et quantification")
    notes = quantifier_notes(transposer(notes, source, cible), tempo_audio, conserver_silence_initial)
    progress(80, "Écriture LilyPond")
    code = generer_lilypond(notes, cible, tempo, mesure)
    dossier = Path(dossier_sortie)
    dossier.mkdir(parents=True, exist_ok=True)
    chemin_ly = dossier / (chemin.stem + '.ly')
    ecrire_lilypond(code, chemin_ly)
    progress(90, "Compilation du PDF")
    pdf = compiler_lilypond(chemin_ly) if compiler_pdf else None
    return {'success': True, 'audio_path': str(chemin), 'lilypond_path': str(chemin_ly),
            'pdf_path': pdf, 'lilypond_code': code, 'tonalite_origine': source,
            'tonalite_cible': cible, 'tempo': tempo, 'tempo_source': tempo_audio,
            'tempo_source_estime': tempo_source is None, 'mesure': list(mesure),
            'decalage_demitons': intervalle_transposition(source, cible),
            'origine_secondes': origine, 'ticks_par_noire': 4, 'nombre_notes': len(notes), 'notes': notes}
