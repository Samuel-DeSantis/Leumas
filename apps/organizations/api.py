from ninja import Router

from .api_auth import get_org_and_membership
from .models import Membership, Organization
from .schemas import MembershipOut, OrganizationIn, OrganizationOut

router = Router(tags=["organizations"])


@router.get("/", response=list[OrganizationOut])
def list_organizations(request):
    return [m.organization for m in Membership.objects.filter(user=request.user).select_related("organization")]


@router.post("/", response=OrganizationOut)
def create_organization(request, payload: OrganizationIn):
    organization = Organization.objects.create(name=payload.name)
    Membership.objects.create(organization=organization, user=request.user, role=Membership.Role.OWNER)
    return organization


@router.get("/{org_slug}/members/", response=list[MembershipOut])
def list_members(request, org_slug: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return Membership.objects.filter(organization=organization).select_related("user")
