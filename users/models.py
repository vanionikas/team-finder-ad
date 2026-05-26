from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .constants import ABOUT_MAX_LENGTH, PHONE_MAX_LENGTH, SKILL_NAME_MAX_LENGTH, USER_NAME_MAX_LENGTH
from .managers import UserManager
from .utils import generate_user_avatar


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True)
    github_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name='users')
    favorites = models.ManyToManyField(
        'projects.Project', blank=True, related_name='favorited_by'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = generate_user_avatar(self.name[0] if self.name else '?')
        super().save(*args, **kwargs)
