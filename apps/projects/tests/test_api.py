import pytest

pytestmark = pytest.mark.django_db


def test_list_projects_via_api(owner_client, organization, project):
    resp = owner_client.get(f"/api/v1/organizations/{organization.slug}/projects/")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert project.name in names


def test_create_project_via_api(engineer_client, organization):
    resp = engineer_client.post(
        f"/api/v1/organizations/{organization.slug}/projects/",
        data={"name": "API Created Project"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "API Created Project"


def test_viewer_cannot_create_project_via_api(viewer_client, organization):
    resp = viewer_client.post(
        f"/api/v1/organizations/{organization.slug}/projects/",
        data={"name": "Blocked Project"},
        content_type="application/json",
    )
    assert resp.status_code == 403


def test_get_single_project_via_api(owner_client, project):
    resp = owner_client.get(f"/api/v1/organizations/{project.organization.slug}/projects/{project.id}/")
    assert resp.status_code == 200
    assert resp.json()["name"] == project.name


def test_delete_project_via_api(owner_client, project):
    resp = owner_client.delete(f"/api/v1/organizations/{project.organization.slug}/projects/{project.id}/")
    assert resp.status_code == 200
    from apps.projects.models import Project

    assert not Project.objects.filter(pk=project.pk).exists()
