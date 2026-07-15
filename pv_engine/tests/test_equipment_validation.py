from dataclasses import replace
from decimal import Decimal

from pv_engine.equipment.domain import CableTypeSpec, ModuleTypeSpec, PCSTypeSpec
from pv_engine.validation.equipment import (
    validate_cable_type,
    validate_module_type,
    validate_pcs_type,
)


def _valid_module_type() -> ModuleTypeSpec:
    return ModuleTypeSpec(
        manufacturer="JinkoSolar",
        model="Tiger Neo 585",
        pmax_w=Decimal("585"),
        vmpp_v=Decimal("34.5"),
        impp_a=Decimal("16.96"),
        voc_v=Decimal("41.9"),
        isc_a=Decimal("17.98"),
        temp_coeff_voc_pct_per_c=Decimal("-0.25"),
        temp_coeff_isc_pct_per_c=Decimal("0.04"),
        temp_coeff_pmax_pct_per_c=Decimal("-0.29"),
        max_system_voltage_v=Decimal("1500"),
        series_fuse_rating_a=Decimal("20"),
    )


def _valid_cable_type() -> CableTypeSpec:
    return CableTypeSpec(
        manufacturer="Southwire",
        material="copper",
        conductor_size="4/0 AWG",
        insulation_type="XLPE",
        ampacity_a=Decimal("260"),
        resistance_ohm_per_km=Decimal("0.1608"),
        reactance_ohm_per_km=Decimal("0.0001"),
        temp_rating_c=90,
        voltage_rating_v=Decimal("2000"),
    )


def _valid_pcs_type() -> PCSTypeSpec:
    return PCSTypeSpec(
        manufacturer="Sungrow",
        model="SG3125HV",
        power_rating_kva=Decimal("3125"),
        nominal_ac_voltage_v=Decimal("34500"),
        min_dc_voltage_v=Decimal("500"),
        max_dc_voltage_v=Decimal("1500"),
        mppt_min_voltage_v=Decimal("875"),
        mppt_max_voltage_v=Decimal("1500"),
        max_dc_current_a=Decimal("3960"),
        max_short_circuit_current_a=Decimal("5000"),
        num_mppt=12,
        efficiency_pct=Decimal("99"),
    )


# --- ModuleType --------------------------------------------------------------


def test_valid_module_type_passes():
    result = validate_module_type(_valid_module_type())
    assert result.is_valid
    assert result.errors == []


def test_module_type_voc_must_exceed_vmpp():
    spec = replace(_valid_module_type(), voc_v=Decimal("30"))  # below vmpp
    result = validate_module_type(spec)
    assert not result.is_valid
    assert any(i.code == "module_type.voc_not_greater_than_vmpp" for i in result.errors)


def test_module_type_isc_must_exceed_impp():
    spec = replace(_valid_module_type(), isc_a=Decimal("10"))  # below impp
    result = validate_module_type(spec)
    assert not result.is_valid
    assert any(i.code == "module_type.isc_not_greater_than_impp" for i in result.errors)


def test_module_type_non_positive_pmax_is_error():
    spec = replace(_valid_module_type(), pmax_w=Decimal("0"))
    result = validate_module_type(spec)
    assert not result.is_valid
    assert any(i.code == "module_type.non_positive_value" for i in result.errors)


def test_module_type_positive_voc_temp_coefficient_is_warning_only():
    spec = replace(_valid_module_type(), temp_coeff_voc_pct_per_c=Decimal("0.1"))
    result = validate_module_type(spec)
    assert result.is_valid  # warning only, not an error
    assert any(i.code == "module_type.positive_voc_temp_coefficient" for i in result.warnings)


def test_module_type_fuse_below_isc_is_warning():
    spec = replace(_valid_module_type(), series_fuse_rating_a=Decimal("10"))
    result = validate_module_type(spec)
    assert result.is_valid
    assert any(i.code == "module_type.fuse_rating_below_isc" for i in result.warnings)


# --- CableType -----------------------------------------------------------


def test_valid_cable_type_passes():
    result = validate_cable_type(_valid_cable_type())
    assert result.is_valid


def test_cable_type_invalid_material_is_error():
    spec = replace(_valid_cable_type(), material="unobtainium")
    result = validate_cable_type(spec)
    assert not result.is_valid
    assert any(i.code == "cable_type.invalid_material" for i in result.errors)


def test_cable_type_non_positive_ampacity_is_error():
    spec = replace(_valid_cable_type(), ampacity_a=Decimal("-1"))
    result = validate_cable_type(spec)
    assert not result.is_valid


def test_cable_type_negative_reactance_is_error():
    spec = replace(_valid_cable_type(), reactance_ohm_per_km=Decimal("-0.01"))
    result = validate_cable_type(spec)
    assert not result.is_valid
    assert any(i.code == "cable_type.negative_reactance" for i in result.errors)


# --- PCSType ---------------------------------------------------------------


def test_valid_pcs_type_passes():
    result = validate_pcs_type(_valid_pcs_type())
    assert result.is_valid


def test_pcs_type_min_voltage_must_be_below_max():
    spec = replace(_valid_pcs_type(), min_dc_voltage_v=Decimal("1600"))
    result = validate_pcs_type(spec)
    assert not result.is_valid
    assert any(i.code == "pcs_type.min_voltage_not_below_max" for i in result.errors)


def test_pcs_type_mppt_range_must_be_ordered():
    spec = replace(_valid_pcs_type(), mppt_min_voltage_v=Decimal("1600"))
    result = validate_pcs_type(spec)
    assert not result.is_valid
    assert any(i.code == "pcs_type.mppt_min_not_below_max" for i in result.errors)


def test_pcs_type_mppt_range_outside_dc_range_is_warning():
    spec = replace(_valid_pcs_type(), mppt_max_voltage_v=Decimal("1600"))  # exceeds max_dc_voltage_v
    result = validate_pcs_type(spec)
    assert result.is_valid  # warning only
    assert any(i.code == "pcs_type.mppt_range_outside_dc_range" for i in result.warnings)


def test_pcs_type_invalid_efficiency_is_error():
    spec = replace(_valid_pcs_type(), efficiency_pct=Decimal("150"))
    result = validate_pcs_type(spec)
    assert not result.is_valid
    assert any(i.code == "pcs_type.invalid_efficiency" for i in result.errors)


def test_pcs_type_zero_mppt_count_is_error():
    spec = replace(_valid_pcs_type(), num_mppt=0)
    result = validate_pcs_type(spec)
    assert not result.is_valid
    assert any(i.code == "pcs_type.invalid_mppt_count" for i in result.errors)
