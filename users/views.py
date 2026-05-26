import json
from http import HTTPStatus

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView, ListView, UpdateView

from .constants import AUTOCOMPLETE_LIMIT, USERS_PER_PAGE
from .forms import EditProfileForm, LoginForm, PasswordChangeForm, RegisterForm
from .models import Skill, User
from .service import query_prefix


class LoginView(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('projects:list'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect(self.request.GET.get('next') or reverse('projects:list'))


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('projects:list'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        User.objects.create_user(
            email=form.cleaned_data['email'],
            name=form.cleaned_data['name'],
            surname=form.cleaned_data['surname'],
            password=form.cleaned_data['password'],
        )
        return redirect(reverse('users:login'))


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('projects:list'))


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'users/edit_profile.html'
    form_class = EditProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.request.user.pk})


class ChangePasswordView(DjangoPasswordChangeView):
    template_name = 'users/change_password.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.request.user.pk})


class UserListView(ListView):
    model = User
    template_name = 'users/participants.html'
    paginate_by = USERS_PER_PAGE

    def get_queryset(self):
        qs = User.objects.all()
        active_skill = self.request.GET.get('skill', '')
        if active_skill:
            qs = qs.filter(skills__name=active_skill).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['active_skill'] = self.request.GET.get('skill', '')
        ctx['all_skills'] = (
            Skill.objects.filter(users__isnull=False)
            .values_list('name', flat=True)
            .distinct()
            .order_by('name')
        )
        ctx['query_prefix'] = query_prefix(self.request)
        return ctx


class SkillsAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        skills = (
            Skill.objects.filter(name__istartswith=q)
            .order_by('name')
            .values('id', 'name')[:AUTOCOMPLETE_LIMIT]
        )
        return JsonResponse(list(skills), safe=False)


class AddUserSkillView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated or request.user.id != pk:
            return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)
        data = json.loads(request.body)
        skill_id = data.get('skill_id')
        name = data.get('name', '').strip()
        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            skill, _ = Skill.objects.get_or_create(name=name)
        else:
            return JsonResponse({'error': 'No skill data'}, status=HTTPStatus.BAD_REQUEST)
        request.user.skills.add(skill)
        return JsonResponse({'id': skill.id, 'name': skill.name})


class RemoveUserSkillView(View):
    def post(self, request, pk, skill_id):
        if not request.user.is_authenticated or request.user.id != pk:
            return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)
        skill = get_object_or_404(Skill, pk=skill_id)
        request.user.skills.remove(skill)
        return JsonResponse({'ok': True})
