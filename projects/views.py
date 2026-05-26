from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .constants import PROJECTS_PER_PAGE
from .forms import ProjectForm
from .models import Project
from .service import query_prefix


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        return Project.objects.select_related('owner').prefetch_related('participants')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['projects'] = self.object_list
        ctx['query_prefix'] = query_prefix(self.request)
        return ctx


class ProjectDetailView(DetailView):
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.select_related('owner').prefetch_related('participants')


class CreateProjectView(LoginRequiredMixin, CreateView):
    template_name = 'projects/create-project.html'
    form_class = ProjectForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_edit'] = False
        return ctx

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect(reverse('projects:detail', kwargs={'pk': project.pk}))


class EditProjectView(LoginRequiredMixin, UpdateView):
    template_name = 'projects/create-project.html'
    form_class = ProjectForm

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_edit'] = True
        ctx['project'] = self.object
        return ctx

    def get_success_url(self):
        return reverse('projects:detail', kwargs={'pk': self.object.pk})


class CompleteProjectView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=HTTPStatus.UNAUTHORIZED)
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        if project.status != Project.STATUS_OPEN:
            return JsonResponse({'error': 'Project is already closed'}, status=HTTPStatus.BAD_REQUEST)
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=['status'])
        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ToggleParticipateView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=HTTPStatus.UNAUTHORIZED)
        project = get_object_or_404(Project, pk=pk)
        if request.user == project.owner:
            return JsonResponse({'error': 'Owner cannot participate'}, status=HTTPStatus.BAD_REQUEST)
        if project.participants.filter(pk=request.user.pk).exists():
            project.participants.remove(request.user)
            return JsonResponse({'status': 'ok', 'participant': False})
        project.participants.add(request.user)
        return JsonResponse({'status': 'ok', 'participant': True})
