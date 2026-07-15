from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from . import services
from .forms import (
    DCCircuitForm,
    MVCircuitForm,
    PCSInstanceForm,
    POIForm,
    SiteForm,
    StringForm,
    SubstationForm,
)
from .mixins import DCCircuitRequiredMixin, PCSInstanceRequiredMixin, ProjectRequiredMixin, SiteRequiredMixin
from .models import POI, DCCircuit, MVCircuit, PCSInstance, Site, String, Substation

# --- Site ------------------------------------------------------------------


class SiteListView(ProjectRequiredMixin, ListView):
    template_name = "electrical/site_list.html"
    context_object_name = "sites"

    def get_queryset(self):
        return Site.objects.filter(project=self.project).order_by("name")


class SiteCreateView(ProjectRequiredMixin, CreateView):
    model = Site
    form_class = SiteForm
    template_name = "electrical/site_form.html"
    required_edit = True

    def form_valid(self, form):
        form.instance.project = self.project
        response = super().form_valid(form)
        messages.success(self.request, f'Site "{self.object.name}" created.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.object.pk},
        )


class SiteDetailView(SiteRequiredMixin, DetailView):
    template_name = "electrical/site_detail.html"
    context_object_name = "site_obj"

    def get_object(self, queryset=None):
        return self.site

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pcs_instances"] = self.site.pcs_instances.select_related("pcs_type").order_by("identifier")
        context["substations"] = self.site.substations.order_by("name")
        context["mv_circuits"] = self.site.mv_circuits.select_related("substation").order_by("identifier")
        return context


class SiteUpdateView(SiteRequiredMixin, UpdateView):
    model = Site
    form_class = SiteForm
    template_name = "electrical/site_form.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.site

    def get_success_url(self):
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.object.pk},
        )


class SiteDeleteView(SiteRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.site

    def get_success_url(self):
        messages.success(self.request, f'Site "{self.object.name}" deleted.')
        return reverse(
            "electrical:site_list",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk},
        )


# --- PCSInstance -------------------------------------------------------------


class PCSInstanceCreateView(SiteRequiredMixin, CreateView):
    model = PCSInstance
    form_class = PCSInstanceForm
    template_name = "electrical/pcs_instance_form.html"
    required_edit = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def form_valid(self, form):
        form.instance.site = self.site
        response = super().form_valid(form)
        messages.success(self.request, f'PCS "{self.object.identifier}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:pcs_instance_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.object.pk,
            },
        )


class PCSInstanceDetailView(PCSInstanceRequiredMixin, DetailView):
    template_name = "electrical/pcs_instance_detail.html"
    context_object_name = "pcs_instance_obj"

    def get_object(self, queryset=None):
        return self.pcs_instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dc_circuits"] = self.pcs_instance.dc_circuits.order_by("identifier")
        return context


class PCSInstanceUpdateView(PCSInstanceRequiredMixin, UpdateView):
    model = PCSInstance
    form_class = PCSInstanceForm
    template_name = "electrical/pcs_instance_form.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.pcs_instance

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def get_success_url(self):
        return reverse(
            "electrical:pcs_instance_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.object.pk,
            },
        )


class PCSInstanceDeleteView(PCSInstanceRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.pcs_instance

    def get_success_url(self):
        messages.success(self.request, f'PCS "{self.object.identifier}" deleted.')
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


# --- DCCircuit ---------------------------------------------------------------


class DCCircuitCreateView(PCSInstanceRequiredMixin, CreateView):
    model = DCCircuit
    form_class = DCCircuitForm
    template_name = "electrical/dc_circuit_form.html"
    required_edit = True

    def form_valid(self, form):
        form.instance.pcs_instance = self.pcs_instance
        response = super().form_valid(form)
        messages.success(self.request, f'DC circuit "{self.object.identifier}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:dc_circuit_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
                "dc_id": self.object.pk,
            },
        )


class DCCircuitDetailView(DCCircuitRequiredMixin, DetailView):
    template_name = "electrical/dc_circuit_detail.html"
    context_object_name = "dc_circuit_obj"

    def get_object(self, queryset=None):
        return self.dc_circuit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["strings"] = self.dc_circuit.strings.select_related("module_type").order_by("identifier")
        return context


class DCCircuitUpdateView(DCCircuitRequiredMixin, UpdateView):
    model = DCCircuit
    form_class = DCCircuitForm
    template_name = "electrical/dc_circuit_form.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.dc_circuit

    def get_success_url(self):
        return reverse(
            "electrical:dc_circuit_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
                "dc_id": self.object.pk,
            },
        )


class DCCircuitDeleteView(DCCircuitRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True

    def get_object(self, queryset=None):
        return self.dc_circuit

    def get_success_url(self):
        messages.success(self.request, f'DC circuit "{self.object.identifier}" deleted.')
        return reverse(
            "electrical:pcs_instance_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
            },
        )


# --- String --------------------------------------------------------------


class StringCreateView(DCCircuitRequiredMixin, CreateView):
    model = String
    form_class = StringForm
    template_name = "electrical/string_form.html"
    required_edit = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def form_valid(self, form):
        form.instance.dc_circuit = self.dc_circuit
        response = super().form_valid(form)
        messages.success(self.request, f'String "{self.object.identifier}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:dc_circuit_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
                "dc_id": self.dc_circuit.pk,
            },
        )


class StringUpdateView(DCCircuitRequiredMixin, UpdateView):
    model = String
    form_class = StringForm
    template_name = "electrical/string_form.html"
    required_edit = True
    pk_url_kwarg = "string_id"

    def get_queryset(self):
        return String.objects.filter(dc_circuit=self.dc_circuit)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def get_success_url(self):
        return reverse(
            "electrical:dc_circuit_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
                "dc_id": self.dc_circuit.pk,
            },
        )


class StringDeleteView(DCCircuitRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True
    pk_url_kwarg = "string_id"

    def get_queryset(self):
        return String.objects.filter(dc_circuit=self.dc_circuit)

    def get_success_url(self):
        messages.success(self.request, f'String "{self.object.identifier}" deleted.')
        return reverse(
            "electrical:dc_circuit_detail",
            kwargs={
                "org_slug": self.organization.slug,
                "project_id": self.project.pk,
                "site_id": self.site.pk,
                "pcs_id": self.pcs_instance.pk,
                "dc_id": self.dc_circuit.pk,
            },
        )


# --- Substation ------------------------------------------------------------


class SubstationCreateView(SiteRequiredMixin, CreateView):
    model = Substation
    form_class = SubstationForm
    template_name = "electrical/substation_form.html"
    required_edit = True

    def form_valid(self, form):
        form.instance.site = self.site
        response = super().form_valid(form)
        messages.success(self.request, f'Substation "{self.object.name}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


class SubstationDeleteView(SiteRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True
    pk_url_kwarg = "substation_id"

    def get_queryset(self):
        return Substation.objects.filter(site=self.site)

    def get_success_url(self):
        messages.success(self.request, f'Substation "{self.object.name}" deleted.')
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


# --- MVCircuit ---------------------------------------------------------------


class MVCircuitCreateView(SiteRequiredMixin, CreateView):
    model = MVCircuit
    form_class = MVCircuitForm
    template_name = "electrical/mv_circuit_form.html"
    required_edit = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

    def form_valid(self, form):
        form.instance.site = self.site
        response = super().form_valid(form)
        messages.success(self.request, f'MV circuit "{self.object.identifier}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


class MVCircuitUpdateView(SiteRequiredMixin, UpdateView):
    model = MVCircuit
    form_class = MVCircuitForm
    template_name = "electrical/mv_circuit_form.html"
    required_edit = True
    pk_url_kwarg = "mv_circuit_id"

    def get_queryset(self):
        return MVCircuit.objects.filter(site=self.site)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["site"] = self.site
        return kwargs

    def get_success_url(self):
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


class MVCircuitDeleteView(SiteRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True
    pk_url_kwarg = "mv_circuit_id"

    def get_queryset(self):
        return MVCircuit.objects.filter(site=self.site)

    def get_success_url(self):
        messages.success(self.request, f'MV circuit "{self.object.identifier}" deleted.')
        return reverse(
            "electrical:site_detail",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk, "site_id": self.site.pk},
        )


# --- POI (project-level) ----------------------------------------------------


class POICreateView(ProjectRequiredMixin, CreateView):
    model = POI
    form_class = POIForm
    template_name = "electrical/poi_form.html"
    required_edit = True

    def form_valid(self, form):
        form.instance.project = self.project
        response = super().form_valid(form)
        messages.success(self.request, f'POI "{self.object.name}" added.')
        return response

    def get_success_url(self):
        return reverse(
            "electrical:hierarchy",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk},
        )


class POIDeleteView(ProjectRequiredMixin, DeleteView):
    template_name = "partials/confirm_delete.html"
    required_edit = True
    pk_url_kwarg = "poi_id"

    def get_queryset(self):
        return POI.objects.filter(project=self.project)

    def get_success_url(self):
        messages.success(self.request, f'POI "{self.object.name}" deleted.')
        return reverse(
            "electrical:hierarchy",
            kwargs={"org_slug": self.organization.slug, "project_id": self.project.pk},
        )


# --- Hierarchy overview + validation -----------------------------------------


class HierarchyView(ProjectRequiredMixin, TemplateView):
    """Full electrical hierarchy tree for a project, with an on-demand
    structural validation report (Phase 1: no calculations).
    """

    template_name = "electrical/hierarchy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sites"] = (
            Site.objects.filter(project=self.project)
            .prefetch_related(
                "pcs_instances__pcs_type",
                "pcs_instances__dc_circuits__strings__module_type",
                "mv_circuits__substation",
                "substations",
            )
            .order_by("name")
        )
        context["pois"] = self.project.pois.order_by("name")
        if self.request.GET.get("validate"):
            context["validation_result"] = services.validate_project_hierarchy(self.project)
        return context
