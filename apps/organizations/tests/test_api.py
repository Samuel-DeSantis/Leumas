import pytest

pytestmark = pytest.mark.django_db


def test_list_organizations_via_api(owner_client, organization):
    resp = owner_client.get("/api/v1/organizations/")
    assert resp.status_code == 200
    names = [o["name"] for o in resp.json()]
    assert organization.name in names


def test_create_organization_via_api(owner_client):
    resp = owner_client.post(
        "/api/v1/organizations/", data={"name": "API Org"}, content_type="application/json"
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "API Org"

    from apps.organizations.models import Membership

    assert Membership.objects.filter(organization__name="API Org", role=Membership.Role.OWNER).exists()


def test_list_members_via_api(owner_client, organization, owner_user, engineer_user, viewer_user):
    resp = owner_client.get(f"/api/v1/organizations/{organization.slug}/members/")
    assert resp.status_code == 200
    emails = {m["user_email"] for m in resp.json()}
    assert emails == {owner_user.email, engineer_user.email, viewer_user.email}


def test_anonymous_cannot_list_organizations(client):
    resp = client.get("/api/v1/organizations/")
    assert resp.status_code in (401, 403)
