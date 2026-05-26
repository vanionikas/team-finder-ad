import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

from .models import User

PHONE_RE = re.compile(r'^(\+7|8)\d{10}$')
GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/', re.IGNORECASE)


def _normalize_phone(phone: str) -> str:
    """Convert 8XXXXXXXXXX to +7XXXXXXXXXX."""
    phone = phone.strip()
    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    return phone


def _validate_github_url(value: str) -> None:
    if value and not GITHUB_RE.match(value):
        raise forms.ValidationError('Ссылка должна вести на GitHub (github.com).')


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self._user = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError('Неверный имейл или пароль.')
            self._user = user
        return self.cleaned_data

    def get_user(self):
        return self._user


class RegisterForm(forms.Form):
    name = forms.CharField(
        label='Имя',
        max_length=124,
        widget=forms.TextInput(attrs={'placeholder': 'Иван'}),
    )
    surname = forms.CharField(
        label='Фамилия',
        max_length=124,
        widget=forms.TextInput(attrs={'placeholder': 'Иванов'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@mail.com'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'GitHub',
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'style': 'display:none', 'accept': 'image/*'}),
            'about': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 999 123-45-67'}),
            'github_url': forms.URLInput(
                attrs={'placeholder': 'https://github.com/username'}
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return phone
        if not PHONE_RE.match(phone):
            raise forms.ValidationError(
                'Введите номер в формате +7XXXXXXXXXX или 8XXXXXXXXXX.'
            )
        phone = _normalize_phone(phone)
        qs = User.objects.filter(phone=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Этот номер телефона уже используется.')
        return phone

    def clean_github_url(self):
        value = self.cleaned_data.get('github_url', '')
        _validate_github_url(value)
        return value


class PasswordChangeForm(DjangoPasswordChangeForm):
    pass
