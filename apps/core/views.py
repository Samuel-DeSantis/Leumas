"""Generic organization-scoped CRUD mixins.

These remove boilerplate that would otherwise be repeated across the
equipment app's three near-identical CRUD flows (ModuleType, CableType,
PCSType) and any future org-scoped resource. Combine with
apps.organizations.permissions.OrganizationRequiredMixin.
"""

from django.contrib import messages
from django.views.generic import CreateView, DeleteView, ListView, UpdateView


class OrgScopedQuerysetMixin:
    """Filters get_queryset() (and get_object()) to self.organization."""

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.organization)


class OrgScopedListView(OrgScopedQuerysetMixin, ListView):
    paginate_by = 50


class OrgScopedCreateView(CreateView):
    success_message = "%(name)s created."

    def form_valid(self, form):
        form.instance.organization = self.organization
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {"name": str(self.object)})
        return response


class OrgScopedUpdateView(OrgScopedQuerysetMixin, UpdateView):
    success_message = "%(name)s updated."

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {"name": str(self.object)})
        return response


class OrgScopedDeleteView(OrgScopedQuerysetMixin, DeleteView):
    success_message = "%(name)s deleted."

    def form_valid(self, form):
        name = str(self.object)
        response = super().form_valid(form)
        messages.success(self.request, self.success_message % {"name": name})
        return response
