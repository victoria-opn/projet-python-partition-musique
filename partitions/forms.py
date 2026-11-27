from django.forms import ModelForm
from .models import Job
from pathlib import Path

from django import forms

class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ["audio", "tonalite"]

    def clean_audio(self):
        audio = self.cleaned_data["audio"]
        allowed_extensions = {".wav"}
        if Path(audio.name).suffix.lower() not in allowed_extensions:
            raise forms.ValidationError("Seuls les fichiers WAV sont acceptés.")
        return audio