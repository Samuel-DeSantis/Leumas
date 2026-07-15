"""Role-based permission helpers.

Kept as small pure functions/mixins operating on Django objects directly
(this is web-layer authorization, not engineering domain logic, so it does
not belong in pv_engine).
"""

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Membership, Organization


def get_membership(user, organization: Organization) -> Membership | None:
    if not user.is_authenticated:
        return None
    return Membership.objects.filter(user=user, organization=organization).select_related("organization").first()


class OrganizationRequiredMixin(AccessMixin):
    """Resolves ``self.organization`` and ``self.membership`` from the
    ``org_slug`` URL kwarg, and rejects non-members.

    Set ``required_edit = True`` on a view subclass to additionally require
    edit permissions (Owner/Admin/Engineer). Set
    ``required_manage_members = True`` to restrict to Owner/Admin.
    """

    required_edit = False
    required_manage_members = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.organization = get_object_or_404(Organization, slug=kwargs["org_slug"])
        self.membership = get_membership(request.user, self.organization)

        if self.membership is None:
            raise PermissionDenied("You are not a member of this organization.")
        if self.required_edit and not self.membership.can_edit:
            raise PermissionDenied("Your role does not allow making changes.")
        if self.required_manage_members and not self.membership.can_manage_members:
            raise PermissionDenied("Only owners and admins can manage members.")

        self.setup_scope(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def setup_scope(self, request, *args, **kwargs):
        """Hook for subclasses: resolve further nested objects (project,
        site, ...) here. Called after organization/membership are resolved
        and permission checks pass, but before the view handler runs.
        """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["organization"] = self.organization
        context["membership"] = self.membership
        return context
