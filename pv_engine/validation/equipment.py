"""Basic engineering validation for equipment datasheets.

Phase 1 scope: sanity/consistency checks only (positive values, expected
orderings such as Voc > Vmpp). No electrical calculations (string sizing,
temperature-adjusted voltages, etc.) happen here yet -- those arrive in
later phases and will themselves call into equipment specs like these.
"""

from decimal import Decimal

from pv_engine.equipment.domain import CableTypeSpec, ModuleTypeSpec, PCSTypeSpec

from .base import ValidationResult


def validate_module_type(spec: ModuleTypeSpec) -> ValidationResult:
    result = ValidationResult()
    ref = spec.label

    for field_name in ("pmax_w", "vmpp_v", "impp_a", "voc_v", "isc_a", "max_system_voltage_v"):
        value: Decimal = getattr(spec, field_name)
        if value <= 0:
            result.error(
                "module_type.non_positive_value",
                f"{field_name} must be greater than zero (got {value}).",
                ref,
            )

    if spec.voc_v > 0 and spec.vmpp_v > 0 and spec.voc_v <= spec.vmpp_v:
        result.error(
            "module_type.voc_not_greater_than_vmpp",
            f"Voc ({spec.voc_v} V) must be greater than Vmpp ({spec.vmpp_v} V).",
            ref,
        )

    if spec.isc_a > 0 and spec.impp_a > 0 and spec.isc_a <= spec.impp_a:
        result.error(
            "module_type.isc_not_greater_than_impp",
            f"Isc ({spec.isc_a} A) must be greater than Impp ({spec.impp_a} A).",
            ref,
        )

    if spec.temp_coeff_voc_pct_per_c > 0:
        result.warning(
            "module_type.positive_voc_temp_coefficient",
            "Voc temperature coefficient is normally negative (Voc drops as it gets hotter).",
            ref,
        )

    if spec.series_fuse_rating_a > 0 and spec.isc_a > 0 and spec.series_fuse_rating_a < spec.isc_a:
        result.warning(
            "module_type.fuse_rating_below_isc",
            "Series fuse rating is below Isc; double check this against the datasheet.",
            ref,
        )

    return result


def validate_cable_type(spec: CableTypeSpec) -> ValidationResult:
    result = ValidationResult()
    ref = spec.label

    if spec.material not in ("copper", "aluminum"):
        result.error("cable_type.invalid_material", f"Unknown conductor material '{spec.material}'.", ref)

    for field_name in ("ampacity_a", "resistance_ohm_per_km", "voltage_rating_v"):
        value: Decimal = getattr(spec, field_name)
        if value <= 0:
            result.error(
                "cable_type.non_positive_value",
                f"{field_name} must be greater than zero (got {value}).",
                ref,
            )

    if spec.reactance_ohm_per_km < 0:
        result.error("cable_type.negative_reactance", "Reactance cannot be negative.", ref)

    if spec.temp_rating_c <= 0:
        result.error("cable_type.invalid_temp_rating", "Temperature rating must be positive.", ref)

    return result


def validate_pcs_type(spec: PCSTypeSpec) -> ValidationResult:
    result = ValidationResult()
    ref = spec.label

    for field_name in (
        "power_rating_kva",
        "nominal_ac_voltage_v",
        "max_dc_voltage_v",
        "max_dc_current_a",
        "max_short_circuit_current_a",
    ):
        value: Decimal = getattr(spec, field_name)
        if value <= 0:
            result.error(
                "pcs_type.non_positive_value",
                f"{field_name} must be greater than zero (got {value}).",
                ref,
            )

    if spec.min_dc_voltage_v >= spec.max_dc_voltage_v:
        result.error(
            "pcs_type.min_voltage_not_below_max",
            "Minimum DC voltage must be below maximum DC voltage.",
            ref,
        )

    if spec.mppt_min_voltage_v >= spec.mppt_max_voltage_v:
        result.error(
            "pcs_type.mppt_min_not_below_max",
            "MPPT minimum voltage must be below MPPT maximum voltage.",
            ref,
        )

    if spec.mppt_min_voltage_v < spec.min_dc_voltage_v or spec.mppt_max_voltage_v > spec.max_dc_voltage_v:
        result.warning(
            "pcs_type.mppt_range_outside_dc_range",
            "MPPT voltage range extends outside the PCS's overall DC voltage range.",
            ref,
        )

    if spec.num_mppt <= 0:
        result.error("pcs_type.invalid_mppt_count", "Number of MPPTs must be at least 1.", ref)

    if not (Decimal("0") < spec.efficiency_pct <= Decimal("100")):
        result.error(
            "pcs_type.invalid_efficiency",
            f"Efficiency must be between 0 and 100% (got {spec.efficiency_pct}).",
            ref,
        )

    return result
