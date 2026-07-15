"""Forms for the electrical hierarchy.

Each form scopes its foreign-key querysets to the relevant organization or
site so a user can never wire in equipment or objects from somewhere they
don't have access to -- this is basic validation of connections (Phase 1
scope), enforced at the form layer before pv_engine's hierarchy validation
ever runs.
"""

from typing import cast

from django import forms

from apps.core.forms import StyledModelForm
from apps.equipment.models import ModuleType, PCSType

from .models import POI, DCCircuit, MVCircuit, PCSInstance, Site, String, Substation


class SiteForm(StyledModelForm):
    class Meta:
        model = Site
        fields = ["name", "description", "latitude", "longitude"]


class PCSInstanceForm(StyledModelForm):
    class Meta:
        model = PCSInstance
        fields = ["identifier", "pcs_type"]

    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        cast(forms.ModelChoiceField, self.fields["pcs_type"]).queryset = PCSType.objects.filter(
            organization=organization
        )


class DCCircuitForm(StyledModelForm):
    class Meta:
        model = DCCircuit
        fields = ["identifier", "mppt_number"]


class StringForm(StyledModelForm):
    class Meta:
        model = String
        fields = ["identifier", "module_type", "modules_per_string", "combiner_identifier"]

    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        cast(forms.ModelChoiceField, self.fields["module_type"]).queryset = ModuleType.objects.filter(
            organization=organization
        )


class SubstationForm(StyledModelForm):
    class Meta:
        model = Substation
        fields = ["name"]


class MVCircuitForm(StyledModelForm):
    class Meta:
        model = MVCircuit
        fields = ["identifier", "voltage_kv", "substation", "pcs_instances"]

    def __init__(self, *args, site, **kwargs):
        super().__init__(*args, **kwargs)
        cast(forms.ModelChoiceField, self.fields["substation"]).queryset = Substation.objects.filter(site=site)
        cast(forms.ModelMultipleChoiceField, self.fields["pcs_instances"]).queryset = PCSInstance.objects.filter(
            site=site
        )


class POIForm(StyledModelForm):
    class Meta:
        model = POI
        fields = ["name", "voltage_kv", "utility_name"]
