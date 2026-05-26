from django.conf import settings
from django.db import models

from .constants import PROJECT_NAME_MAX_LENGTH, STATUS_MAX_LENGTH


class Project(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Открыт'),
        (STATUS_CLOSED, 'Закрыт'),
    ]

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(max_length=STATUS_MAX_LENGTH, choices=STATUS_CHOICES, default=STATUS_OPEN)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
    )
    skills = models.ManyToManyField(
        'users.Skill',
        blank=True,
        related_name='projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
