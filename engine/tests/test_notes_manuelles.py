"""Référence indépendante de l'analyse audio : notes, rythmes et code attendus."""
import unittest

from engine.exemple_notes_manuelles import NOTES, convertir_notes
from engine.music import transposer
from engine.lilypond import generer_lilypond


class NotesManuellesTest(unittest.TestCase):
    def test_au_clair_do_vers_re_92(self):
        source = convertir_notes(NOTES)
        notes = transposer(source, 'c', 'd')
        self.assertEqual([(n['nom'], n['octave']) for n in notes],
                         [('re', 4), ('re', 4), ('re', 4), ('mi', 4), ('fa#', 4), ('mi', 4), ('re', 4), ('fa#', 4), ('mi', 4), ('re', 4)])
        self.assertEqual([n['debut_tick'] for n in notes],
                         [0, 4, 8, 12, 16, 24, 32, 36, 40, 48])
        self.assertEqual([n['duree_ticks'] for n in notes],
                         [4, 4, 4, 4, 8, 8, 4, 4, 8, 16])
        code = generer_lilypond(notes, 'd', 92)
        self.assertIn('\\key d \\major', code)
        self.assertIn('\\tempo 4 = 92', code)
        self.assertIn("d'4 d'4 d'4 e'4 | fis'2 e'2 | d'4 fis'4 e'2 | d'1 |", code)

    def test_octave_alterations_et_silence(self):
        source = convertir_notes([('si', 4, .5), ('silence', None, .5),
                                  ('do#', 5, 1), ('mib', 5, 2)])
        notes = transposer(source, 'c', 'd')
        self.assertEqual([(n['nom'], n['octave']) for n in notes], [('do#', 5), ('re#', 5), ('fa', 5)])
        self.assertEqual([n['debut_tick'] for n in notes], [0, 4, 8])
        self.assertIn("cis''8 r8", generer_lilypond(notes, 'd', 92))


if __name__ == '__main__':
    unittest.main()
