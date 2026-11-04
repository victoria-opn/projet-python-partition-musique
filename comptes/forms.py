from pathlib import Path

from django import forms


class AudioUploadForm(forms.Form):
    audio = forms.FileField(
        label="Fichier audio",
        help_text="Formats acceptés : MP3, WAV, OGG, M4A ou FLAC.",
    )

    def clean_audio(self):
        audio = self.cleaned_data["audio"]
        allowed_extensions = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
        if Path(audio.name).suffix.lower() not in allowed_extensions:
            raise forms.ValidationError("Veuillez choisir un fichier audio accepté.")
        return audio
