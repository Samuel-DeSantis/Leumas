import pytest
from django.urls import reverse

from apps.electrical.models import DCCircuit, PCSInstance, Site, String

pytestmark = pytest.mark.django_db


def _kwargs(project, **extra):
    return {"org_slug": project.organization.slug, "project_id": project.id, **extra}


def test_site_create_by_engineer(engineer_client, project):
    url = reverse("electrical:site_create", kwargs=_kwargs(project))
    resp = engineer_client.post(url, {"name": "Site B"})
    assert resp.status_code == 302
    assert Site.objects.filter(project=project, name="Site B").exists()


def test_site_create_forbidden_for_viewer(viewer_client, project):
    url = reverse("electrical:site_create", kwargs=_kwargs(project))
    resp = viewer_client.post(url, {"name": "Site B"})
    assert resp.status_code == 403


def test_pcs_instance_create_scoped_to_org_equipment(engineer_client, project, site, pcs_type):
    url = reverse("electrical:pcs_instance_create", kwargs=_kwargs(project, site_id=site.id))
    resp = engineer_client.post(url, {"identifier": "INV-02", "pcs_type": str(pcs_type.id)})
    assert resp.status_code == 302
    assert PCSInstance.objects.filter(site=site, identifier="INV-02").exists()


def test_dc_circuit_create_under_pcs_instance(engineer_client, project, site, pcs_instance):
    url = reverse(
        "electrical:dc_circuit_create",
        kwargs=_kwargs(project, site_id=site.id, pcs_id=pcs_instance.id),
    )
    resp = engineer_client.post(url, {"identifier": "MPPT-2", "mppt_number": "2"})
    assert resp.status_code == 302
    assert DCCircuit.objects.filter(pcs_instance=pcs_instance, identifier="MPPT-2").exists()


def test_string_create_under_dc_circuit(engineer_client, project, site, pcs_instance, dc_circuit, module_type):
    url = reverse(
        "electrical:string_create",
        kwargs=_kwargs(project, site_id=site.id, pcs_id=pcs_instance.id, dc_id=dc_circuit.id),
    )
    resp = engineer_client.post(
        url,
        {
            "identifier": "STR-2",
            "module_type": str(module_type.id),
            "modules_per_string": "26",
            "combiner_identifier": "CMB-1",
        },
    )
    assert resp.status_code == 302
    assert String.objects.filter(dc_circuit=dc_circuit, identifier="STR-2").exists()


def test_site_from_wrong_project_returns_404(engineer_client, project, site, make_user, organization):
    from apps.projects.models import Project

    other_project = Project.objects.create(organization=organization, name="Other Project")
    url = reverse("electrical:site_detail", kwargs=_kwargs(other_project, site_id=site.id))
    resp = engineer_client.get(url)
    assert resp.status_code == 404


def test_hierarchy_view_renders_without_validation_by_default(owner_client, project, string_obj):
    url = reverse("electrical:hierarchy", kwargs=_kwargs(project))
    resp = owner_client.get(url)
    assert resp.status_code == 200
    assert "validation_result" not in resp.context


def test_hierarchy_view_runs_validation_when_requested(owner_client, project, string_obj):
    url = reverse("electrical:hierarchy", kwargs=_kwargs(project))
    resp = owner_client.get(url, {"validate": "1"})
    assert resp.status_code == 200
    assert resp.context["validation_result"].is_valid


def test_hierarchy_view_shows_errors_for_invalid_design(owner_client, project, dc_circuit, module_type):
    String.objects.create(
        dc_circuit=dc_circuit, module_type=module_type, identifier="BAD", modules_per_string=0
    )
    url = reverse("electrical:hierarchy", kwargs=_kwargs(project))
    resp = owner_client.get(url, {"validate": "1"})
    assert resp.status_code == 200
    result = resp.context["validation_result"]
    assert not result.is_valid
    assert b"error" in resp.content.lower()
