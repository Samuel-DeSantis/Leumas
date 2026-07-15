"""Shared helpers for Django Ninja endpoints that need organization-scoped
authorization. Mirrors the logic in apps.organizations.permissions, but as
plain functions (Ninja views are function-based, not class-based).
"""

from ninja.errors import HttpError

from .models import Membership, Organization
from .permissions import get_membership


def get_org_and_membership(request, org_slug: str, *, required_edit: bool = False) -> tuple[Organization, Membership]:
    try:
        organization = Organization.objects.get(slug=org_slug)
    except Organization.DoesNotExist:
        raise HttpError(404, "Organization not found.") from None

    membership = get_membership(request.user, organization)
    if membership is None:
        raise HttpError(403, "You are not a member of this organization.")
    if required_edit and not membership.can_edit:
        raise HttpError(403, "Your role does not allow making changes.")
    return organization, membership
