from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('list', views.UserListView.as_view(), name='list'),
    path('edit-profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('skills/', views.SkillsAutocompleteView.as_view(), name='skills_autocomplete'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('<int:pk>/skills/add/', views.AddUserSkillView.as_view(), name='add_skill'),
    path(
        '<int:pk>/skills/<int:skill_id>/remove/',
        views.RemoveUserSkillView.as_view(),
        name='remove_skill',
    ),
]
