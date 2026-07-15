"""Equipment forms.

Basic field-level validation (required, positive numbers via model field
constraints) is handled by Django. Cross-field engineering sanity checks
(Voc > Vmpp, MPPT range within DC range, etc.) are delegated to pv_engine
through apps.equipment.services, per Rule 1-3 in CLAUDE.md: engineering
logic never lives in views or models.
"""

from django import forms

from apps.core.forms import TailwindStyledFormMixin
from pv_engine.validation.base import ValidationResult

from . import services
from .models import CableType, ModuleType, PCSType


class _PVEngineValidatedForm(TailwindStyledFormMixin, forms.ModelForm):
    """Adds a ``pv_engine_warnings`` list (non-blocking) after cleaning.

    ERROR-level pv_engine issues are attached as form errors and block
    submission; WARNING-level issues are surfaced to the template but do
    not block saving.
    """

    def get_pv_engine_validation(self, cleaned_data: dict) -> ValidationResult:
        """Override in each subclass to call the matching
        services.validate_*_fields function."""
        return ValidationResult()

    def clean(self):
        cleaned_data = super().clean() or {}
        self.pv_engine_warnings: list[str] = []
        if self.errors:
            # Don't run cross-field engineering checks on top of missing/invalid fields.
            return cleaned_data
        result = self.get_pv_engine_validation(cleaned_data)
        for issue in result.errors:
            self.add_error(None, issue.message)
        self.pv_engine_warnings = [issue.message for issue in result.warnings]
        return cleaned_data


class ModuleTypeForm(_PVEngineValidatedForm):
    def get_pv_engine_validation(self, cleaned_data: dict) -> ValidationResult:
        return services.validate_module_type_fields(cleaned_data)

    class Meta:
        model = ModuleType
        fields = [
            "manufacturer",
            "model",
            "pmax_w",
            "vmpp_v",
            "impp_a",
            "voc_v",
            "isc_a",
            "temp_coeff_voc_pct_per_c",
            "temp_coeff_isc_pct_per_c",
            "temp_coeff_pmax_pct_per_c",
            "length_mm",
            "width_mm",
            "depth_mm",
            "weight_kg",
            "max_system_voltage_v",
            "series_fuse_rating_a",
        ]


class CableTypeForm(_PVEngineValidatedForm):
    def get_pv_engine_validation(self, cleaned_data: dict) -> ValidationResult:
        return services.validate_cable_type_fields(cleaned_data)

    class Meta:
        model = CableType
        fields = [
            "manufacturer",
            "material",
            "conductor_size",
            "insulation_type",
            "ampacity_a",
            "resistance_ohm_per_km",
            "reactance_ohm_per_km",
            "temp_rating_c",
            "voltage_rating_v",
            "cost_per_meter",
        ]


class PCSTypeForm(_PVEngineValidatedForm):
    def get_pv_engine_validation(self, cleaned_data: dict) -> ValidationResult:
        return services.validate_pcs_type_fields(cleaned_data)

    class Meta:
        model = PCSType
        fields = [
            "manufacturer",
            "model",
            "power_rating_kva",
            "nominal_ac_voltage_v",
            "min_dc_voltage_v",
            "max_dc_voltage_v",
            "mppt_min_voltage_v",
            "mppt_max_voltage_v",
            "max_dc_current_a",
            "max_short_circuit_current_a",
            "num_mppt",
            "efficiency_pct",
            "has_integrated_transformer",
        ]
