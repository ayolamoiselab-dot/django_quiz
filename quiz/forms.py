# forms.py
from django import forms
from .models import TemporaryCategory

class TemporaryCategoryForm(forms.ModelForm):
    class Meta:
        model = TemporaryCategory
        fields = ['titre', 'description', 'niveau', 'nombre_questions']
