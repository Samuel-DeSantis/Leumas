import pytest
from django.urls import reverse

from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_project_list_shows_only_own_organization_projects(owner_client, organization, project, make_user):
    from apps.organizations.models import Membership, Organization

    other_org = Organization.objects.create(name="Other Co")
    other_user = make_user(email="other-owner@example.com")
    Membership.objects.create(organization=other_org, user=other_user, role=Membership.Role.OWNER)
    Project.objects.create(organization=other_org, name="Someone Else's Project")

    url = reverse("projects:list", kwargs={"org_slug": organization.slug})
    resp = owner_client.get(url)
    assert resp.status_code == 200
    names = [p.name for p in resp.context["projects"]]
    assert "Sunbelt 100MW" in names
    assert "Someone Else's Project" not in names


def test_viewer_cannot_create_project(viewer_client, organization):
    url = reverse("projects:create", kwargs={"org_slug": organization.slug})
    resp = viewer_client.post(url, {"name": "New Project"})
    assert resp.status_code == 403
    assert not Project.objects.filter(name="New Project").exists()


def test_engineer_can_create_project(engineer_client, organization):
    url = reverse("projects:create", kwargs={"org_slug": organization.slug})
    resp = engineer_client.post(url, {"name": "New Project", "description": "", "location": ""})
    assert resp.status_code == 302
    assert Project.objects.filter(name="New Project", organization=organization).exists()


def test_project_detail_requires_membership(client, project, make_user):
    outsider = make_user(email="outsider@example.com")
    client.force_login(outsider)
    url = reverse(
        "projects:detail", kwargs={"org_slug": project.organization.slug, "project_id": project.id}
    )
    resp = client.get(url)
    assert resp.status_code == 403


def test_project_delete_by_owner(owner_client, project):
    url = reverse(
        "projects:delete", kwargs={"org_slug": project.organization.slug, "project_id": project.id}
    )
    resp = owner_client.post(url)
    assert resp.status_code == 302
    assert not Project.objects.filter(pk=project.pk).exists()
