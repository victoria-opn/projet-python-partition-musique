import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
from scipy.io import wavfile

from engine.interface_backend import generer_partition
from engine.notes import note_vers_frequence, frequence_vers_note
from engine.music import nom_lilypond, transposer
from engine.audio import analyser_audio, quantifier_notes, frequence_fondamentale
from engine.lilypond import generer_lilypond


class TranscriptionTest(unittest.TestCase):
    def test_wav_harmoniques_octaves_rythmes(self):
        fs = 22050
        morceaux = [np.zeros(int(fs * .25))]
        attendus = [('do', 4, .5), ('do', 5, .25), ('si', 4, .75), ('la', 4, .5)]
        for nom, octave, duree in attendus:
            t = np.arange(round(fs * duree)) / fs
            f = note_vers_frequence(nom, octave)
            # Deuxième harmonique plus forte que la fondamentale.
            son = .2 * np.sin(2*np.pi*f*t) + .5 * np.sin(4*np.pi*f*t)
            morceaux.append(son)
            morceaux.append(np.zeros(round(fs * .125)))
        signal = np.concatenate(morceaux)
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'melodie.wav'
            # Stéréo avec canaux opposés : aucune annulation à la lecture.
            wavfile.write(chemin, fs, np.column_stack((signal, -signal)).astype(np.float32))
            notes = analyser_audio(chemin)
            self.assertEqual([(n['nom'], n['octave']) for n in notes], [(nom, oct) for nom, oct, _ in attendus])
            for note, (_, _, duree) in zip(notes, attendus):
                self.assertAlmostEqual(note['fin'] - note['debut'], duree, delta=.04)
            resultat = generer_partition(chemin, tonalite_cible='c', dossier_sortie=dossier, compiler_pdf=False, tempo=120)
            json.dumps(resultat)
            self.assertEqual([n['duree_ticks'] for n in resultat['notes']], [4, 2, 6, 4])
            self.assertNotIn('<', resultat['lilypond_code'])
            self.assertIsNone(resultat['pdf_path'])
            transpose = generer_partition(chemin, 'g', 120, dossier_sortie=dossier,
                                          tonalite_source='c', compiler_pdf=False)
            self.assertEqual(transpose['decalage_demitons'], -5)
            self.assertEqual([(n['nom_source'], n['octave_source']) for n in transpose['notes']], [('do', 4), ('do', 5), ('si', 4), ('la', 4)])
            self.assertEqual([(n['nom'], n['octave']) for n in transpose['notes']], [('sol', 3), ('sol', 4), ('fa#', 4), ('mi', 4)])
            self.assertIn('g4', transpose['lilypond_code'])
            self.assertIn("fis'4.", transpose['lilypond_code'])
            rapide = generer_partition(chemin, 'g', 180, dossier_sortie=dossier,
                                       tonalite_source='c', compiler_pdf=False)
            self.assertEqual(rapide['notes'], transpose['notes'])
            self.assertIn('\\tempo 4 = 180', rapide['lilypond_code'])
            self.assertAlmostEqual(rapide['tempo_source'], 120, delta=3)
            impose = generer_partition(chemin, 'g', 180, dossier_sortie=dossier,
                                       tonalite_source='c', tempo_source=120, compiler_pdf=False)
            self.assertFalse(impose['tempo_source_estime'])
            self.assertEqual([n['duree_ticks'] for n in impose['notes']], [4, 2, 6, 4])

    def test_notes_repetees(self):
        fs = 16000
        t = np.arange(7200) / fs
        note = .5 * np.sin(2*np.pi*440*t)
        signal = np.concatenate([note, np.zeros(800), note])
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'repete.wav'
            wavfile.write(chemin, fs, signal.astype(np.float32))
            self.assertEqual([(n['nom'], n['octave']) for n in analyser_audio(chemin)], [('la', 4), ('la', 4)])

    def test_silence(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / 'silence.wav'
            wavfile.write(chemin, 16000, np.zeros(16000, dtype=np.int16))
            with self.assertRaisesRegex(ValueError, 'Aucune note'):
                analyser_audio(chemin)

    def test_transposition_et_orthographe(self):
        note = transposer([{'nom': 'si', 'octave': 4}], 'c', 'd')[0]
        self.assertEqual((note['nom'], note['octave']), ('do#', 5))
        self.assertEqual(nom_lilypond('do', 4, 'c'), "c'")
        self.assertEqual(nom_lilypond('do', 4, 'cis'), 'bis')
        self.assertEqual(nom_lilypond('si', 3, 'ces'), "ces'")

    def test_mesures_liaisons_silences(self):
        notes = [{'nom': 'do', 'octave': 4, 'debut_tick': 2, 'duree_ticks': 18}]
        code = generer_lilypond(notes, 'c')
        self.assertIn("r8 c'2.~ c'8~ | c'4", code)
        self.assertNotIn('None', code)
        self.assertIn('r2.', code)
        for signature in [(3, 4), (6, 8)]:
            self.assertIn('\\time ' + '/'.join(map(str, signature)), generer_lilypond(notes, 'c', mesure=signature))

    def test_grille_alignee_sur_premiere_attaque(self):
        notes = [dict(nom="do", octave=4, debut=2.07, fin=2.55),
                 dict(nom="re", octave=4, debut=2.57, fin=3.06),
                 dict(nom="mi", octave=4, debut=3.07, fin=4.07)]
        quantifiees = quantifier_notes(notes, 120)
        self.assertEqual([n['debut_tick'] for n in quantifiees], [0, 4, 8])
        self.assertEqual([n['duree_ticks'] for n in quantifiees], [4, 4, 8])
        self.assertEqual(quantifiees[0]['debut'], 2.07)
        self.assertEqual(quantifier_notes(notes, 120, True)[0]['debut_tick'], 17)

    def test_articulation_courte_et_vrai_silence(self):
        notes = [dict(nom="do", octave=4, debut=0, fin=.56),
                 dict(nom="do", octave=4, debut=.59, fin=1.09),
                 dict(nom="re", octave=4, debut=1.34, fin=1.84)]
        a, b, c = quantifier_notes(notes, 120)
        self.assertEqual(a['debut_tick'] + a['duree_ticks'], b['debut_tick'])
        self.assertGreater(c['debut_tick'], b['debut_tick'] + b['duree_ticks'])

    def test_fft_et_table_frequences(self):
        fs = 16000
        t = np.arange(1600) / fs
        for nom, octave in [('do', 3), ('si', 3), ('do', 4), ('la', 4), ('do', 5), ('do', 7)]:
            with self.subTest(nom=nom, octave=octave):
                f = note_vers_frequence(nom, octave)
                signal = .2 * np.sin(2*np.pi*f*t) + .5 * np.sin(4*np.pi*f*t)
                trouvee = frequence_fondamentale(signal, fs)
                self.assertAlmostEqual(trouvee, f, delta=1)
                self.assertEqual(frequence_vers_note(trouvee), (nom, octave))
        self.assertEqual(note_vers_frequence('la', 4), 440)
        self.assertAlmostEqual(note_vers_frequence('do', 4), 261.625565, places=5)

    def test_tempo_invalide(self):
        with self.assertRaises(ValueError):
            quantifier_notes([], 0)


if __name__ == '__main__':
    unittest.main()
