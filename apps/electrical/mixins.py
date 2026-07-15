"""Mixins that resolve nested electrical-hierarchy resources from URL
kwargs, each scoped to its parent so a user can never reach an object
outside their organization/project/site (basic validation of connections,
Phase 1 scope).

Chain: Organization -> Project -> Site -> PCSInstance -> DCCircuit

Each mixin adds one level of nesting and extends setup_scope() (see
apps.organizations.permissions.OrganizationRequiredMixin), which runs
after the organization/membership/permission checks succeed.
"""

from django.shortcuts import get_object_or_404

from apps.organizations.permissions import OrganizationRequiredMixin
from apps.projects.models import Project

from .models import DCCircuit, PCSInstance, Site


class ProjectRequiredMixin(OrganizationRequiredMixin):
    def setup_scope(self, request, *args, **kwargs):
        super().setup_scope(request, *args, **kwargs)
        self.project = get_object_or_404(
            Project, pk=kwargs["project_id"], organization=self.organization
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


class SiteRequiredMixin(ProjectRequiredMixin):
    def setup_scope(self, request, *args, **kwargs):
        super().setup_scope(request, *args, **kwargs)
        self.site = get_object_or_404(Site, pk=kwargs["site_id"], project=self.project)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site"] = self.site
        return context


class PCSInstanceRequiredMixin(SiteRequiredMixin):
    def setup_scope(self, request, *args, **kwargs):
        super().setup_scope(request, *args, **kwargs)
        self.pcs_instance = get_object_or_404(PCSInstance, pk=kwargs["pcs_id"], site=self.site)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pcs_instance"] = self.pcs_instance
        return context


class DCCircuitRequiredMixin(PCSInstanceRequiredMixin):
    def setup_scope(self, request, *args, **kwargs):
        super().setup_scope(request, *args, **kwargs)
        self.dc_circuit = get_object_or_404(
            DCCircuit, pk=kwargs["dc_id"], pcs_instance=self.pcs_instance
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dc_circuit"] = self.dc_circuit
        return context
