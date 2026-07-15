"""Shared fixtures for the whole suite.

pytest-django provides ``db``/``client`` already; these fixtures build the
domain objects (organization, membership, project, equipment, electrical
hierarchy) that most tests need, so individual test modules stay short.
"""

from decimal import Decimal

import pytest

from apps.accounts.models import User
from apps.electrical.models import DCCircuit, PCSInstance, Site, String
from apps.equipment.models import CableType, ModuleType, PCSType
from apps.organizations.models import Membership, Organization
from apps.projects.models import Project


@pytest.fixture
def make_user(db):
    def _make_user(email="user@example.com", **kwargs):
        return User.objects.create_user(email=email, password="test-pass-123", **kwargs)

    return _make_user


@pytest.fixture
def owner_user(make_user):
    return make_user(email="owner@example.com", first_name="Olivia", last_name="Owner")


@pytest.fixture
def engineer_user(make_user):
    return make_user(email="engineer@example.com", first_name="Eli", last_name="Engineer")


@pytest.fixture
def viewer_user(make_user):
    return make_user(email="viewer@example.com", first_name="Vic", last_name="Viewer")


@pytest.fixture
def organization(db, owner_user, engineer_user, viewer_user):
    org = Organization.objects.create(name="Acme Solar")
    Membership.objects.create(organization=org, user=owner_user, role=Membership.Role.OWNER)
    Membership.objects.create(organization=org, user=engineer_user, role=Membership.Role.ENGINEER)
    Membership.objects.create(organization=org, user=viewer_user, role=Membership.Role.VIEWER)
    return org


@pytest.fixture
def owner_client(client, owner_user):
    client.force_login(owner_user)
    return client


@pytest.fixture
def engineer_client(client, engineer_user):
    client.force_login(engineer_user)
    return client


@pytest.fixture
def viewer_client(client, viewer_user):
    client.force_login(viewer_user)
    return client


@pytest.fixture
def project(organization, owner_user):
    return Project.objects.create(organization=organization, name="Sunbelt 100MW", created_by=owner_user)


@pytest.fixture
def module_type(organization):
    return ModuleType.objects.create(
        organization=organization,
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


@pytest.fixture
def cable_type(organization):
    return CableType.objects.create(
        organization=organization,
        manufacturer="Southwire",
        material=CableType.Material.COPPER,
        conductor_size="4/0 AWG",
        insulation_type="XLPE",
        ampacity_a=Decimal("260"),
        resistance_ohm_per_km=Decimal("0.1608"),
        reactance_ohm_per_km=Decimal("0.0001"),
        temp_rating_c=90,
        voltage_rating_v=Decimal("2000"),
    )


@pytest.fixture
def pcs_type(organization):
    return PCSType.objects.create(
        organization=organization,
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


@pytest.fixture
def site(project):
    return Site.objects.create(project=project, name="Site A")


@pytest.fixture
def pcs_instance(site, pcs_type):
    return PCSInstance.objects.create(site=site, pcs_type=pcs_type, identifier="INV-01")


@pytest.fixture
def dc_circuit(pcs_instance):
    return DCCircuit.objects.create(pcs_instance=pcs_instance, identifier="MPPT-1", mppt_number=1)


@pytest.fixture
def string_obj(dc_circuit, module_type):
    return String.objects.create(
        dc_circuit=dc_circuit, module_type=module_type, identifier="STR-1", modules_per_string=28
    )
