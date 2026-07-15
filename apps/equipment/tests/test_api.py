import pytest

pytestmark = pytest.mark.django_db

VALID_MODULE_PAYLOAD = {
    "manufacturer": "Trina Solar",
    "model": "Vertex S+ API",
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


def test_list_module_types_requires_membership(client, organization, module_type, make_user):
    outsider = make_user(email="api-outsider@example.com")
    client.force_login(outsider)
    resp = client.get(f"/api/v1/organizations/{organization.slug}/equipment/module-types/")
    assert resp.status_code == 403


def test_list_module_types(owner_client, organization, module_type):
    resp = owner_client.get(f"/api/v1/organizations/{organization.slug}/equipment/module-types/")
    assert resp.status_code == 200
    data = resp.json()
    assert any(m["model"] == module_type.model for m in data)


def test_create_module_type_requires_edit_permission(viewer_client, organization):
    resp = viewer_client.post(
        f"/api/v1/organizations/{organization.slug}/equipment/module-types/",
        data=VALID_MODULE_PAYLOAD,
        content_type="application/json",
    )
    assert resp.status_code == 403


def test_create_module_type_success(engineer_client, organization):
    resp = engineer_client.post(
        f"/api/v1/organizations/{organization.slug}/equipment/module-types/",
        data=VALID_MODULE_PAYLOAD,
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["model"] == "Vertex S+ API"


def test_create_module_type_rejects_invalid_engineering_data(engineer_client, organization):
    bad_payload = {**VALID_MODULE_PAYLOAD, "voc_v": "10"}  # below vmpp
    resp = engineer_client.post(
        f"/api/v1/organizations/{organization.slug}/equipment/module-types/",
        data=bad_payload,
        content_type="application/json",
    )
    assert resp.status_code == 422


def test_delete_module_type(engineer_client, organization, module_type):
    resp = engineer_client.delete(
        f"/api/v1/organizations/{organization.slug}/equipment/module-types/{module_type.id}/"
    )
    assert resp.status_code == 200
    assert resp.json() == {"success": True}
