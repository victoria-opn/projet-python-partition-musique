"""Contrat moteur P3 utilisé par la tâche Celery de P2."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
from .interface_backend import generer_partition as transcrire

class AudioInvalideError(ValueError):
    pass

class LilypondError(RuntimeError):
    pass

def generer_partition(fichier_audio, tonalite_cible, output, on_progress=None, *, tempo=120):
    """Écrit le PDF à output et retourne son chemin ; tempo final optionnel."""
    target = Path(output).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    # Un espace temporaire par appel évite les collisions, même avec le même WAV.
    with TemporaryDirectory(prefix="partition-") as directory:
        try:
            result = transcrire(fichier_audio, tonalite_cible, tempo,
                                dossier_sortie=directory, on_progress=on_progress)
        except (ValueError, OSError) as exc:
            raise AudioInvalideError("Le fichier audio ou les paramètres sont invalides.") from exc
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            raise LilypondError("La compilation LilyPond a échoué ou dépassé le délai autorisé.") from exc
        shutil.copyfile(result["pdf_path"], target)
    if on_progress:
        on_progress(100, "Partition prête")
    return str(target)
