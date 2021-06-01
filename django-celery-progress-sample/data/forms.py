from django import forms
from django.forms.models import ModelForm
from .models import *

class FileInfoForm(forms.ModelForm):
    """Form definition for FileInfo."""

    class Meta:
        """Meta definition for FileInfoform."""

        model = FileInfo
        fields = ('file',)

# class ImportFileForm(forms.Form):
#     document_file = forms.FileField()