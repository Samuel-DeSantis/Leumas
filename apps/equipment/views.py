from django.db.models import Q
from django.urls import reverse
from django.views.generic import TemplateView

from apps.core.views import (
    OrgScopedCreateView,
    OrgScopedDeleteView,
    OrgScopedListView,
    OrgScopedUpdateView,
)
from apps.organizations.permissions import OrganizationRequiredMixin

from .forms import CableTypeForm, ModuleTypeForm, PCSTypeForm
from .models import CableType, ModuleType, PCSType


class EquipmentLibraryHomeView(OrganizationRequiredMixin, TemplateView):
    template_name = "equipment/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module_type_count"] = ModuleType.objects.filter(organization=self.organization).count()
        context["cable_type_count"] = CableType.objects.filter(organization=self.organization).count()
        context["pcs_type_count"] = PCSType.objects.filter(organization=self.organization).count()
        return context


class _SearchableMixin:
    """Adds ?q= search across search_fields. When the request comes from
    HTMX (live search-as-you-type), only the results table partial is
    rendered instead of the full page.
    """

    search_fields: tuple[str, ...] = ("manufacturer", "model")
    table_partial_template: str = ""

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            q_filter = Q()
            for field_name in self.search_fields:
                q_filter |= Q(**{f"{field_name}__icontains": query})
            queryset = queryset.filter(q_filter)
        return queryset.order_by(*self.model._meta.ordering)

    def get_template_names(self):
        if getattr(self.request, "htmx", False) and self.table_partial_template:
            return [self.table_partial_template]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


# --- ModuleType ---------------------------------------------------------


class ModuleTypeListView(OrganizationRequiredMixin, _SearchableMixin, OrgScopedListView):
    model = ModuleType
    template_name = "equipment/module_type_list.html"
    table_partial_template = "equipment/_module_type_table.html"
    context_object_name = "module_types"


class ModuleTypeCreateView(OrganizationRequiredMixin, OrgScopedCreateView):
    model = ModuleType
    form_class = ModuleTypeForm
    template_name = "equipment/module_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:module_type_list", kwargs={"org_slug": self.organization.slug})


class ModuleTypeUpdateView(OrganizationRequiredMixin, OrgScopedUpdateView):
    model = ModuleType
    form_class = ModuleTypeForm
    template_name = "equipment/module_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:module_type_list", kwargs={"org_slug": self.organization.slug})


class ModuleTypeDeleteView(OrganizationRequiredMixin, OrgScopedDeleteView):
    model = ModuleType
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:module_type_list", kwargs={"org_slug": self.organization.slug})


# --- CableType -----------------------------------------------------------


class CableTypeListView(OrganizationRequiredMixin, _SearchableMixin, OrgScopedListView):
    model = CableType
    template_name = "equipment/cable_type_list.html"
    table_partial_template = "equipment/_cable_type_table.html"
    context_object_name = "cable_types"
    search_fields = ("manufacturer", "conductor_size")


class CableTypeCreateView(OrganizationRequiredMixin, OrgScopedCreateView):
    model = CableType
    form_class = CableTypeForm
    template_name = "equipment/cable_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:cable_type_list", kwargs={"org_slug": self.organization.slug})


class CableTypeUpdateView(OrganizationRequiredMixin, OrgScopedUpdateView):
    model = CableType
    form_class = CableTypeForm
    template_name = "equipment/cable_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:cable_type_list", kwargs={"org_slug": self.organization.slug})


class CableTypeDeleteView(OrganizationRequiredMixin, OrgScopedDeleteView):
    model = CableType
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:cable_type_list", kwargs={"org_slug": self.organization.slug})


# --- PCSType ---------------------------------------------------------------


class PCSTypeListView(OrganizationRequiredMixin, _SearchableMixin, OrgScopedListView):
    model = PCSType
    template_name = "equipment/pcs_type_list.html"
    table_partial_template = "equipment/_pcs_type_table.html"
    context_object_name = "pcs_types"


class PCSTypeCreateView(OrganizationRequiredMixin, OrgScopedCreateView):
    model = PCSType
    form_class = PCSTypeForm
    template_name = "equipment/pcs_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:pcs_type_list", kwargs={"org_slug": self.organization.slug})


class PCSTypeUpdateView(OrganizationRequiredMixin, OrgScopedUpdateView):
    model = PCSType
    form_class = PCSTypeForm
    template_name = "equipment/pcs_type_form.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:pcs_type_list", kwargs={"org_slug": self.organization.slug})


class PCSTypeDeleteView(OrganizationRequiredMixin, OrgScopedDeleteView):
    model = PCSType
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_success_url(self):
        return reverse("equipment:pcs_type_list", kwargs={"org_slug": self.organization.slug})
