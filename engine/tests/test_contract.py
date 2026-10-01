from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from engine.engine import generer_partition, AudioInvalideError, LilypondError

class EngineContractTests(unittest.TestCase):
    def test_pdf_at_requested_location(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'nested' / 'score.pdf'
            def transcribe(audio, tonalite, tempo, dossier_sortie, on_progress):
                generated = Path(dossier_sortie) / 'input.pdf'
                generated.write_bytes(b'%PDF-1.4')
                on_progress(45, 'Notes')
                return {'pdf_path': str(generated)}
            steps = []
            with patch('engine.engine.transcrire', side_effect=transcribe):
                result = generer_partition('test.wav', 'd', target, lambda p, label: steps.append(p))
            self.assertEqual(result, str(target.resolve()))
            self.assertTrue(target.read_bytes().startswith(b'%PDF'))
            self.assertEqual(steps, [45, 100])
    def test_clear_errors(self):
        for error, expected in [(ValueError('audio'), AudioInvalideError), (RuntimeError('lilypond'), LilypondError)]:
            with tempfile.TemporaryDirectory() as directory, patch('engine.engine.transcrire', side_effect=error):
                with self.assertRaises(expected):
                    generer_partition('test.wav', 'c', Path(directory) / 'score.pdf')
