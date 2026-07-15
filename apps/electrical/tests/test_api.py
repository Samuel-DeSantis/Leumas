import pytest

pytestmark = pytest.mark.django_db


def _base(project):
    return f"/api/v1/organizations/{project.organization.slug}/projects/{project.id}"


def test_get_hierarchy_tree(owner_client, project, string_obj):
    resp = owner_client.get(f"{_base(project)}/hierarchy/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sites"]) == 1
    assert len(data["sites"][0]["pcs_instances"]) == 1


def test_validate_hierarchy_endpoint_valid(owner_client, project, string_obj):
    resp = owner_client.get(f"{_base(project)}/hierarchy/validate/")
    assert resp.status_code == 200
    assert resp.json()["is_valid"] is True


def test_validate_hierarchy_endpoint_invalid(owner_client, project, dc_circuit, module_type):
    from apps.electrical.models import String

    String.objects.create(dc_circuit=dc_circuit, module_type=module_type, identifier="BAD", modules_per_string=0)
    resp = owner_client.get(f"{_base(project)}/hierarchy/validate/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is False
    assert any(issue["code"] == "string.invalid_module_count" for issue in data["issues"])


def test_create_site_via_api(engineer_client, project):
    resp = engineer_client.post(f"{_base(project)}/sites/", data={"name": "API Site"}, content_type="application/json")
    assert resp.status_code == 200
    assert resp.json()["name"] == "API Site"


def test_create_string_via_api(engineer_client, project, site, pcs_instance, dc_circuit, module_type):
    url = (
        f"{_base(project)}/sites/{site.id}/pcs/{pcs_instance.id}/dc-circuits/{dc_circuit.id}/strings/"
    )
    resp = engineer_client.post(
        url,
        data={
            "identifier": "API-STR-1",
            "module_type_id": str(module_type.id),
            "modules_per_string": 24,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()["modules_per_string"] == 24


def test_viewer_cannot_create_site_via_api(viewer_client, project):
    resp = viewer_client.post(f"{_base(project)}/sites/", data={"name": "Blocked Site"}, content_type="application/json")
    assert resp.status_code == 403
