import pytest

from apps.electrical import services
from apps.electrical.models import String

pytestmark = pytest.mark.django_db


def test_build_hierarchy_spec_reflects_orm_structure(project, site, pcs_instance, dc_circuit, string_obj):
    spec = services.build_hierarchy_spec(project)

    assert spec.project_id == str(project.id)
    assert len(spec.sites) == 1
    site_spec = spec.sites[0]
    assert site_spec.name == "Site A"
    assert len(site_spec.pcs_instances) == 1

    pcs_spec = site_spec.pcs_instances[0]
    assert pcs_spec.identifier == "INV-01"
    assert len(pcs_spec.dc_circuits) == 1

    dc_spec = pcs_spec.dc_circuits[0]
    assert dc_spec.identifier == "MPPT-1"
    assert len(dc_spec.strings) == 1

    string_spec = dc_spec.strings[0]
    assert string_spec.identifier == "STR-1"
    assert string_spec.modules_per_string == 28


def test_validate_project_hierarchy_valid_case(project, string_obj):
    result = services.validate_project_hierarchy(project)
    assert result.is_valid, [i.message for i in result.errors]


def test_validate_project_hierarchy_catches_zero_module_string(project, dc_circuit, module_type):
    String.objects.create(
        dc_circuit=dc_circuit, module_type=module_type, identifier="BAD-STR", modules_per_string=0
    )
    result = services.validate_project_hierarchy(project)
    assert not result.is_valid
    assert any(i.code == "string.invalid_module_count" for i in result.errors)


def test_validate_project_hierarchy_catches_cross_org_equipment(
    project, dc_circuit, make_user
):
    from decimal import Decimal

    from apps.equipment.models import ModuleType
    from apps.organizations.models import Organization

    other_org = Organization.objects.create(name="Other Co")
    other_module_type = ModuleType.objects.create(
        organization=other_org,
        manufacturer="Foreign",
        model="Import-1",
        pmax_w=Decimal("400"),
        vmpp_v=Decimal("30"),
        impp_a=Decimal("13"),
        voc_v=Decimal("37"),
        isc_a=Decimal("14"),
        temp_coeff_voc_pct_per_c=Decimal("-0.3"),
        temp_coeff_isc_pct_per_c=Decimal("0.05"),
        temp_coeff_pmax_pct_per_c=Decimal("-0.35"),
        max_system_voltage_v=Decimal("1500"),
        series_fuse_rating_a=Decimal("15"),
    )
    String.objects.create(
        dc_circuit=dc_circuit, module_type=other_module_type, identifier="STR-X", modules_per_string=20
    )
    result = services.validate_project_hierarchy(project)
    assert not result.is_valid
    assert any(i.code == "string.cross_organization_equipment" for i in result.errors)


def test_empty_project_hierarchy_is_valid(project):
    result = services.validate_project_hierarchy(project)
    assert result.is_valid
    assert len(result.issues) == 0
