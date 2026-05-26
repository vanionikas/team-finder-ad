from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None):
        if not email:
            raise ValueError('Email обязателен')
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            surname=surname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password):
        user = self.create_user(email, name, surname, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    about = models.TextField(max_length=256, blank=True)
    phone = models.CharField(max_length=12, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.avatar:
            from .utils import generate_user_avatar
            self.avatar = generate_user_avatar(self.name[0] if self.name else '?')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} {self.surname}'

    class Meta:
        ordering = ['-date_joined']
