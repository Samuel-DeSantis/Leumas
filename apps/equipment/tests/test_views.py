import pytest
from django.urls import reverse

from apps.equipment.models import ModuleType

pytestmark = pytest.mark.django_db

VALID_MODULE_DATA = {
    "manufacturer": "Trina Solar",
    "model": "Vertex S+",
    "pmax_w": "500",
    "vmpp_v": "32",
    "impp_a": "15.6",
    "voc_v": "38",
    "isc_a": "16.5",
    "temp_coeff_voc_pct_per_c": "-0.25",
    "temp_coeff_isc_pct_per_c": "0.04",
    "temp_coeff_pmax_pct_per_c": "-0.34",
    "max_system_voltage_v": "1500",
    "series_fuse_rating_a": "20",
}


def test_viewer_can_list_but_not_create(viewer_client, organization, module_type):
    list_url = reverse("equipment:module_type_list", kwargs={"org_slug": organization.slug})
    resp = viewer_client.get(list_url)
    assert resp.status_code == 200
    assert module_type in resp.context["module_types"]

    create_url = reverse("equipment:module_type_create", kwargs={"org_slug": organization.slug})
    resp = viewer_client.post(create_url, VALID_MODULE_DATA)
    assert resp.status_code == 403


def test_engineer_can_create_module_type(engineer_client, organization):
    create_url = reverse("equipment:module_type_create", kwargs={"org_slug": organization.slug})
    resp = engineer_client.post(create_url, VALID_MODULE_DATA)
    assert resp.status_code == 302
    obj = ModuleType.objects.get(model="Vertex S+")
    assert obj.organization == organization


def test_module_type_search_filters_results(owner_client, organization, module_type):
    list_url = reverse("equipment:module_type_list", kwargs={"org_slug": organization.slug})
    resp = owner_client.get(list_url, {"q": "jinko"})
    assert module_type in resp.context["module_types"]

    resp = owner_client.get(list_url, {"q": "no-such-manufacturer"})
    assert module_type not in resp.context["module_types"]


def test_module_type_htmx_search_returns_partial_only(owner_client, organization, module_type):
    list_url = reverse("equipment:module_type_list", kwargs={"org_slug": organization.slug})
    resp = owner_client.get(list_url, {"q": "jinko"}, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    # Partial should not include the full page shell (no <html> tag)
    assert b"<html" not in resp.content
    assert module_type.model.encode() in resp.content


def test_module_type_delete_by_engineer(engineer_client, organization, module_type):
    url = reverse("equipment:module_type_delete", kwargs={"org_slug": organization.slug, "pk": module_type.id})
    resp = engineer_client.post(url)
    assert resp.status_code == 302
    assert not ModuleType.objects.filter(pk=module_type.pk).exists()


def test_cannot_access_another_organizations_equipment(owner_client, module_type, make_user):
    from apps.organizations.models import Membership, Organization

    other_org = Organization.objects.create(name="Other Co")
    other_owner = make_user(email="other-org-owner@example.com")
    Membership.objects.create(organization=other_org, user=other_owner, role=Membership.Role.OWNER)

    url = reverse("equipment:module_type_edit", kwargs={"org_slug": other_org.slug, "pk": module_type.id})
    owner_client.force_login(other_owner)
    resp = owner_client.get(url)
    assert resp.status_code == 404
