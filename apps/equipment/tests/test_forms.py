from apps.equipment.forms import ModuleTypeForm, PCSTypeForm

VALID_MODULE_DATA = {
    "manufacturer": "JinkoSolar",
    "model": "Tiger Neo 585",
    "pmax_w": "585",
    "vmpp_v": "34.5",
    "impp_a": "16.96",
    "voc_v": "41.9",
    "isc_a": "17.98",
    "temp_coeff_voc_pct_per_c": "-0.25",
    "temp_coeff_isc_pct_per_c": "0.04",
    "temp_coeff_pmax_pct_per_c": "-0.29",
    "max_system_voltage_v": "1500",
    "series_fuse_rating_a": "20",
}


def test_valid_module_type_form_is_valid():
    form = ModuleTypeForm(data=VALID_MODULE_DATA)
    assert form.is_valid(), form.errors
    assert form.pv_engine_warnings == []


def test_module_type_form_blocks_on_voc_below_vmpp():
    data = {**VALID_MODULE_DATA, "voc_v": "20"}
    form = ModuleTypeForm(data=data)
    assert not form.is_valid()
    assert "greater than Vmpp" in str(form.errors)


def test_module_type_form_surfaces_warning_without_blocking():
    data = {**VALID_MODULE_DATA, "temp_coeff_voc_pct_per_c": "0.1"}
    form = ModuleTypeForm(data=data)
    assert form.is_valid()
    assert any("Voc temperature coefficient" in w for w in form.pv_engine_warnings)


def test_pcs_type_form_blocks_on_inverted_dc_voltage_range():
    data = {
        "manufacturer": "Sungrow",
        "model": "SG3125HV",
        "power_rating_kva": "3125",
        "nominal_ac_voltage_v": "34500",
        "min_dc_voltage_v": "1600",  # invalid: above max
        "max_dc_voltage_v": "1500",
        "mppt_min_voltage_v": "875",
        "mppt_max_voltage_v": "1500",
        "max_dc_current_a": "3960",
        "max_short_circuit_current_a": "5000",
        "num_mppt": "12",
        "efficiency_pct": "99",
        "has_integrated_transformer": False,
    }
    form = PCSTypeForm(data=data)
    assert not form.is_valid()
