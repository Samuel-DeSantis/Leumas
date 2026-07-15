from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.electrical.models import Site
from apps.organizations.permissions import OrganizationRequiredMixin

from .forms import ProjectForm
from .models import Project


class ProjectListView(OrganizationRequiredMixin, ListView):
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(organization=self.organization).order_by("-created_at")


class ProjectCreateView(OrganizationRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create.html"
    required_edit = True

    def form_valid(self, form):
        form.instance.organization = self.organization
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Project "{self.object.name}" created.')
        return response

    def get_success_url(self):
        return reverse(
            "projects:detail", kwargs={"org_slug": self.organization.slug, "project_id": self.object.pk}
        )


class ProjectDetailMixin(OrganizationRequiredMixin):
    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs["project_id"], organization=self.organization)


class ProjectDetailView(ProjectDetailMixin, DetailView):
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_object(self, queryset=None):
        return self.get_project()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sites"] = Site.objects.filter(project=self.object).order_by("name")
        return context


class ProjectUpdateView(ProjectDetailMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/edit.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.get_project()

    def get_success_url(self):
        return reverse(
            "projects:detail", kwargs={"org_slug": self.organization.slug, "project_id": self.object.pk}
        )


class ProjectDeleteView(ProjectDetailMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.get_project()

    def get_success_url(self):
        messages.success(self.request, f'Project "{self.object.name}" deleted.')
        return reverse("projects:list", kwargs={"org_slug": self.organization.slug})
