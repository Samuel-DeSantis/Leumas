"""Resolves the "current organization" from the URL for use in navigation.

Access control itself is enforced by OrganizationRequiredMixin at the view
level; this middleware only makes the organization available cheaply to
templates (e.g. for the nav bar) without every view needing to pass it
explicitly.
"""

from .models import Organization


class CurrentOrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        org_slug = view_kwargs.get("org_slug")
        if org_slug:
            request.organization = Organization.objects.filter(slug=org_slug).first()
        return None
