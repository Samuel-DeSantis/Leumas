import pytest
from django.urls import reverse

from apps.organizations.models import Membership

pytestmark = pytest.mark.django_db


def test_anonymous_user_redirected_to_login(client, organization):
    url = reverse("organizations:dashboard", kwargs={"org_slug": organization.slug})
    resp = client.get(url)
    assert resp.status_code == 302
    assert reverse("accounts:login") in resp.url


def test_non_member_gets_403(client, organization, make_user):
    outsider = make_user(email="outsider@example.com")
    client.force_login(outsider)
    url = reverse("organizations:dashboard", kwargs={"org_slug": organization.slug})
    resp = client.get(url)
    assert resp.status_code == 403


def test_member_can_view_dashboard(viewer_client, organization):
    url = reverse("organizations:dashboard", kwargs={"org_slug": organization.slug})
    resp = viewer_client.get(url)
    assert resp.status_code == 200


def test_viewer_cannot_add_member(viewer_client, organization, make_user):
    make_user(email="new.engineer@example.com")
    url = reverse("organizations:add_member", kwargs={"org_slug": organization.slug})
    resp = viewer_client.post(url, {"email": "new.engineer@example.com", "role": Membership.Role.ENGINEER})
    assert resp.status_code == 403


def test_owner_can_add_existing_user_as_member(owner_client, organization, make_user):
    new_user = make_user(email="new.engineer@example.com")
    url = reverse("organizations:add_member", kwargs={"org_slug": organization.slug})
    resp = owner_client.post(url, {"email": "new.engineer@example.com", "role": Membership.Role.ENGINEER})
    assert resp.status_code == 302
    assert Membership.objects.filter(organization=organization, user=new_user).exists()


def test_adding_member_with_unknown_email_fails_validation(owner_client, organization):
    url = reverse("organizations:add_member", kwargs={"org_slug": organization.slug})
    resp = owner_client.post(url, {"email": "ghost@example.com", "role": Membership.Role.ENGINEER})
    assert resp.status_code == 200  # re-rendered with form error
    assert not Membership.objects.filter(organization=organization, user__email="ghost@example.com").exists()


def test_last_owner_cannot_be_removed(owner_client, organization, owner_user):
    membership = Membership.objects.get(organization=organization, user=owner_user)
    url = reverse(
        "organizations:remove_member", kwargs={"org_slug": organization.slug, "membership_id": membership.id}
    )
    resp = owner_client.post(url)
    assert resp.status_code == 403
    assert Membership.objects.filter(pk=membership.pk).exists()


def test_engineer_can_be_removed_by_owner(owner_client, organization, engineer_user):
    membership = Membership.objects.get(organization=organization, user=engineer_user)
    url = reverse(
        "organizations:remove_member", kwargs={"org_slug": organization.slug, "membership_id": membership.id}
    )
    resp = owner_client.post(url)
    assert resp.status_code == 302
    assert not Membership.objects.filter(pk=membership.pk).exists()
