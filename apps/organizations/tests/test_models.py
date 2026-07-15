import pytest
from django.db import IntegrityError

from apps.organizations.models import Membership, Organization

pytestmark = pytest.mark.django_db


def test_organization_slug_auto_generated():
    org = Organization.objects.create(name="Acme Solar")
    assert org.slug == "acme-solar"


def test_organization_slug_unique_suffix_on_slug_collision():
    # Different names that slugify to the same value (name itself is
    # unique, so this is the only way slugs can actually collide).
    Organization.objects.create(name="Acme Solar")
    org2 = Organization.objects.create(name="Acme Solar!!")
    assert org2.slug == "acme-solar-2"


def test_membership_role_permissions(organization, owner_user, engineer_user, viewer_user):
    owner_membership = Membership.objects.get(organization=organization, user=owner_user)
    engineer_membership = Membership.objects.get(organization=organization, user=engineer_user)
    viewer_membership = Membership.objects.get(organization=organization, user=viewer_user)

    assert owner_membership.can_edit
    assert owner_membership.can_manage_members
    assert owner_membership.can_delete_organization

    assert engineer_membership.can_edit
    assert not engineer_membership.can_manage_members
    assert not engineer_membership.can_delete_organization

    assert not viewer_membership.can_edit
    assert not viewer_membership.can_manage_members


def test_membership_unique_per_user_and_org(organization, owner_user):
    with pytest.raises(IntegrityError):
        Membership.objects.create(organization=organization, user=owner_user, role=Membership.Role.VIEWER)
