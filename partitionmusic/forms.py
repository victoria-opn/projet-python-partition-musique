import os
from django import forms

TONALITES = [
    "C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F",
    "Am", "Em", "Bm", "F#m", "C#m", "G#m", "Dm", "Gm", "Cm", "Fm",
]  # à adapter aux valeurs acceptées par le moteur de P3
MAX_SIZE = 20 * 1024 * 1024  # 20 Mo


class JobForm(forms.Form):
    audio = forms.FileField()
    tonalite = forms.ChoiceField(choices=[(t, t) for t in TONALITES])

    def clean_audio(self):
        f = self.cleaned_data["audio"]
        if os.path.splitext(f.name)[1].lower() != ".wav":
            raise forms.ValidationError("Format non supporté : seuls les fichiers .wav sont acceptés.")
        if f.size > MAX_SIZE:
            raise forms.ValidationError("Fichier trop volumineux (20 Mo maximum).")
        return f