import json

from django.contrib.auth import login, logout, update_session_auth_hash
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import EditProfileForm, LoginForm, PasswordChangeForm, RegisterForm
from .models import Skill, User

USERS_PER_PAGE = 12
AUTOCOMPLETE_LIMIT = 10


def _query_prefix(request, exclude='page'):
    params = request.GET.copy()
    params.pop(exclude, None)
    qs = params.urlencode()
    return (qs + '&') if qs else ''


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/projects/list')
        return render(request, 'users/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get('next', '/projects/list'))
        return render(request, 'users/login.html', {'form': form})


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/projects/list')
        return render(request, 'users/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                password=form.cleaned_data['password'],
            )
            return redirect('/users/login/')
        return render(request, 'users/register.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/projects/list')


class UserDetailView(View):
    def get(self, request, pk):
        profile_user = get_object_or_404(User, pk=pk)
        return render(request, 'users/user-details.html', {'user': profile_user})


class EditProfileView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/?next=/users/edit-profile/')
        form = EditProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/')
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/users/{request.user.id}/')
        return render(request, 'users/edit_profile.html', {'form': form})


class ChangePasswordView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/?next=/users/change-password/')
        form = PasswordChangeForm(request.user)
        return render(request, 'users/change_password.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/')
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            return redirect(f'/users/{request.user.id}/')
        return render(request, 'users/change_password.html', {'form': form})


class UserListView(View):
    def get(self, request):
        users_qs = User.objects.all().order_by('-date_joined')
        active_skill = request.GET.get('skill', '')

        if active_skill:
            users_qs = users_qs.filter(skills__name=active_skill).distinct()

        all_skills = (
            Skill.objects.filter(users__isnull=False)
            .values_list('name', flat=True)
            .distinct()
            .order_by('name')
        )

        paginator = Paginator(users_qs, USERS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'users/participants.html', {
            'page_obj': page_obj,
            'active_skill': active_skill,
            'all_skills': all_skills,
            'query_prefix': _query_prefix(request),
        })


class SkillsAutocompleteView(View):
    def get(self, request):
        q = request.GET.get('q', '').strip()
        skills = (
            Skill.objects.filter(name__istartswith=q).order_by('name').values('id', 'name')[:AUTOCOMPLETE_LIMIT]
        )
        return JsonResponse(list(skills), safe=False)


class AddUserSkillView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated or request.user.id != pk:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        data = json.loads(request.body)
        skill_id = data.get('skill_id')
        name = data.get('name', '').strip()
        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        elif name:
            skill, _ = Skill.objects.get_or_create(name=name)
        else:
            return JsonResponse({'error': 'No skill data'}, status=400)
        request.user.skills.add(skill)
        return JsonResponse({'id': skill.id, 'name': skill.name})


class RemoveUserSkillView(View):
    def post(self, request, pk, skill_id):
        if not request.user.is_authenticated or request.user.id != pk:
            return JsonResponse({'error': 'Forbidden'}, status=403)
        skill = get_object_or_404(Skill, pk=skill_id)
        request.user.skills.remove(skill)
        return JsonResponse({'ok': True})
