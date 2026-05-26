from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .forms import ProjectForm
from .models import Project

PROJECTS_PER_PAGE = 12


def _query_prefix(request, exclude='page'):
    params = request.GET.copy()
    params.pop(exclude, None)
    qs = params.urlencode()
    return (qs + '&') if qs else ''


class ProjectListView(View):
    def get(self, request):
        projects_qs = Project.objects.select_related('owner').prefetch_related(
            'participants'
        ).order_by('-created_at')

        paginator = Paginator(projects_qs, PROJECTS_PER_PAGE)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        return render(request, 'projects/project_list.html', {
            'page_obj': page_obj,
            'projects': projects_qs,
            'query_prefix': _query_prefix(request),
        })


class ProjectDetailView(View):
    def get(self, request, pk):
        project = get_object_or_404(
            Project.objects.select_related('owner').prefetch_related('participants'),
            pk=pk,
        )
        return render(request, 'projects/project-details.html', {'project': project})


class CreateProjectView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/?next=/projects/create-project')
        return render(request, 'projects/create-project.html', {
            'form': ProjectForm(),
            'is_edit': False,
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('/users/login/')
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect(f'/projects/{project.id}')
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': False,
        })


class EditProjectView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect(f'/users/login/?next=/projects/{pk}/edit')
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        form = ProjectForm(instance=project)
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True,
            'project': project,
        })

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('/users/login/')
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect(f'/projects/{project.id}')
        return render(request, 'projects/create-project.html', {
            'form': form,
            'is_edit': True,
            'project': project,
        })


class CompleteProjectView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        if project.status != Project.STATUS_OPEN:
            return JsonResponse({'error': 'Project is already closed'}, status=400)
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=['status'])
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ToggleParticipateView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        project = get_object_or_404(Project, pk=pk)
        if request.user == project.owner:
            return JsonResponse({'error': 'Owner cannot participate'}, status=400)
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            return JsonResponse({'status': 'ok', 'participant': False})
        else:
            project.participants.add(request.user)
            return JsonResponse({'status': 'ok', 'participant': True})
