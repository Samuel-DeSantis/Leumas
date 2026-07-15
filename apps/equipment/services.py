"""Bridge between Django ORM equipment models and pv_engine.

Rule (CLAUDE.md): "Views call services. Services call the engineering
engine." Views/forms should import from here, never from pv_engine
directly, and pv_engine should never import Django models.
"""

from pv_engine.equipment.domain import CableTypeSpec, ModuleTypeSpec, PCSTypeSpec
from pv_engine.validation.base import ValidationResult
from pv_engine.validation.equipment import (
    validate_cable_type,
    validate_module_type,
    validate_pcs_type,
)

from .models import CableType, ModuleType, PCSType


def to_module_type_spec(obj: ModuleType) -> ModuleTypeSpec:
    return ModuleTypeSpec(
        manufacturer=obj.manufacturer,
        model=obj.model,
        pmax_w=obj.pmax_w,
        vmpp_v=obj.vmpp_v,
        impp_a=obj.impp_a,
        voc_v=obj.voc_v,
        isc_a=obj.isc_a,
        temp_coeff_voc_pct_per_c=obj.temp_coeff_voc_pct_per_c,
        temp_coeff_isc_pct_per_c=obj.temp_coeff_isc_pct_per_c,
        temp_coeff_pmax_pct_per_c=obj.temp_coeff_pmax_pct_per_c,
        max_system_voltage_v=obj.max_system_voltage_v,
        series_fuse_rating_a=obj.series_fuse_rating_a,
    )


def to_cable_type_spec(obj: CableType) -> CableTypeSpec:
    return CableTypeSpec(
        manufacturer=obj.manufacturer,
        material=obj.material,
        conductor_size=obj.conductor_size,
        insulation_type=obj.insulation_type,
        ampacity_a=obj.ampacity_a,
        resistance_ohm_per_km=obj.resistance_ohm_per_km,
        reactance_ohm_per_km=obj.reactance_ohm_per_km,
        temp_rating_c=obj.temp_rating_c,
        voltage_rating_v=obj.voltage_rating_v,
    )


def to_pcs_type_spec(obj: PCSType) -> PCSTypeSpec:
    return PCSTypeSpec(
        manufacturer=obj.manufacturer,
        model=obj.model,
        power_rating_kva=obj.power_rating_kva,
        nominal_ac_voltage_v=obj.nominal_ac_voltage_v,
        min_dc_voltage_v=obj.min_dc_voltage_v,
        max_dc_voltage_v=obj.max_dc_voltage_v,
        mppt_min_voltage_v=obj.mppt_min_voltage_v,
        mppt_max_voltage_v=obj.mppt_max_voltage_v,
        max_dc_current_a=obj.max_dc_current_a,
        max_short_circuit_current_a=obj.max_short_circuit_current_a,
        num_mppt=obj.num_mppt,
        efficiency_pct=obj.efficiency_pct,
    )


def validate_module_type_instance(obj: ModuleType) -> ValidationResult:
    return validate_module_type(to_module_type_spec(obj))


def validate_cable_type_instance(obj: CableType) -> ValidationResult:
    return validate_cable_type(to_cable_type_spec(obj))


def validate_pcs_type_instance(obj: PCSType) -> ValidationResult:
    return validate_pcs_type(to_pcs_type_spec(obj))


# --- Form-time validation ---------------------------------------------
# Forms validate cleaned_data *before* an instance is saved. Spec field
# names intentionally match the model/form field names so cleaned_data can
# be passed straight through.


def validate_module_type_fields(cleaned_data: dict) -> ValidationResult:
    # Dynamic construction from a cleaned_data dict whose keys match the
    # dataclass field names by design (tested in apps/equipment/tests);
    # mypy can't verify this statically.
    spec = ModuleTypeSpec(**{f: cleaned_data.get(f) for f in ModuleTypeSpec.__dataclass_fields__})  # type: ignore[arg-type]
    return validate_module_type(spec)


def validate_cable_type_fields(cleaned_data: dict) -> ValidationResult:
    spec = CableTypeSpec(**{f: cleaned_data.get(f) for f in CableTypeSpec.__dataclass_fields__})  # type: ignore[arg-type]
    return validate_cable_type(spec)


def validate_pcs_type_fields(cleaned_data: dict) -> ValidationResult:
    spec = PCSTypeSpec(**{f: cleaned_data.get(f) for f in PCSTypeSpec.__dataclass_fields__})  # type: ignore[arg-type]
    return validate_pcs_type(spec)
