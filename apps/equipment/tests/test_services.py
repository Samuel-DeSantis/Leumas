import pytest

from apps.equipment import services

pytestmark = pytest.mark.django_db


def test_to_module_type_spec_round_trips_fields(module_type):
    spec = services.to_module_type_spec(module_type)
    assert spec.manufacturer == module_type.manufacturer
    assert spec.model == module_type.model
    assert spec.pmax_w == module_type.pmax_w
    assert spec.voc_v == module_type.voc_v


def test_validate_module_type_instance_valid(module_type):
    result = services.validate_module_type_instance(module_type)
    assert result.is_valid


def test_validate_cable_type_instance_valid(cable_type):
    result = services.validate_cable_type_instance(cable_type)
    assert result.is_valid


def test_validate_pcs_type_instance_valid(pcs_type):
    result = services.validate_pcs_type_instance(pcs_type)
    assert result.is_valid


def test_validate_module_type_fields_catches_bad_data():
    bad_data = {
        "manufacturer": "Acme",
        "model": "Bad Module",
        "pmax_w": 400,
        "vmpp_v": 40,
        "impp_a": 10,
        "voc_v": 30,  # lower than vmpp: invalid
        "isc_a": 11,
        "temp_coeff_voc_pct_per_c": -0.3,
        "temp_coeff_isc_pct_per_c": 0.05,
        "temp_coeff_pmax_pct_per_c": -0.3,
        "max_system_voltage_v": 1500,
        "series_fuse_rating_a": 15,
    }
    result = services.validate_module_type_fields(bad_data)
    assert not result.is_valid
