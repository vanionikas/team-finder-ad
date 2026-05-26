from django import forms

from core.mixins import GithubUrlMixin
from .models import Project


class ProjectForm(GithubUrlMixin, forms.ModelForm):
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
