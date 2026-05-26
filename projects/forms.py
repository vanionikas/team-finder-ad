import re

from django import forms

from .models import Project

GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/', re.IGNORECASE)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Название вашего проекта'}),
            'description': forms.Textarea(
                attrs={'rows': 6, 'placeholder': 'Опишите ваш проект...'}
            ),
            'github_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/username/repo'}
            ),
        }

    def clean_github_url(self):
        value = self.cleaned_data.get('github_url', '')
        if value and not GITHUB_RE.match(value):
            raise forms.ValidationError('Ссылка должна вести на GitHub (github.com).')
        return value
