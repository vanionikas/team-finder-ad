from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Skill, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'surname', 'is_staff', 'date_joined')
    search_fields = ('email', 'name', 'surname')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {
            'fields': ('name', 'surname', 'avatar', 'about', 'phone', 'github_url'),
        }),
        ('Навыки', {'fields': ('skills',)}),
        ('Избранное', {'fields': ('favorites',)}),
        ('Права', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ('skills', 'favorites', 'groups', 'user_permissions')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
