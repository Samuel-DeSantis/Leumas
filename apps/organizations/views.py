from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, View

from .forms import AddMemberForm, OrganizationForm
from .models import Membership, Organization
from .permissions import OrganizationRequiredMixin


class OrganizationSelectView(LoginRequiredMixin, ListView):
    """Landing page after login: pick an organization or create one."""

    template_name = "organizations/select.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return (
            Membership.objects.filter(user=self.request.user)
            .select_related("organization")
            .order_by("organization__name")
        )


class OrganizationCreateView(LoginRequiredMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    template_name = "organizations/create.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        Membership.objects.create(
            organization=self.object,
            user=self.request.user,
            role=Membership.Role.OWNER,
        )
        messages.success(self.request, f'Organization "{self.object.name}" created.')
        return response

    def get_success_url(self):
        return reverse("organizations:dashboard", kwargs={"org_slug": self.object.slug})


class OrganizationDashboardView(OrganizationRequiredMixin, DetailView):
    template_name = "organizations/dashboard.html"
    context_object_name = "organization"

    def get_object(self, queryset=None):
        return self.organization


class MemberListView(OrganizationRequiredMixin, ListView):
    template_name = "organizations/members.html"
    context_object_name = "members"

    def get_queryset(self):
        return (
            Membership.objects.filter(organization=self.organization)
            .select_related("user")
            .order_by("role", "user__email")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_member_form"] = AddMemberForm(organization=self.organization)
        return context


class AddMemberView(OrganizationRequiredMixin, FormView):
    form_class = AddMemberForm
    template_name = "organizations/members.html"
    required_manage_members = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organization"] = self.organization
        return kwargs

    def form_valid(self, form):
        Membership.objects.create(
            organization=self.organization,
            user=form.user,
            role=form.cleaned_data["role"],
        )
        messages.success(self.request, f"Added {form.user.email} to the organization.")
        return redirect("organizations:members", org_slug=self.organization.slug)

    def form_invalid(self, form):
        members = (
            Membership.objects.filter(organization=self.organization)
            .select_related("user")
            .order_by("role", "user__email")
        )
        return self.render_to_response(
            self.get_context_data(members=members, add_member_form=form)
        )


class RemoveMemberView(OrganizationRequiredMixin, View):
    required_manage_members = True

    def post(self, request, org_slug, membership_id):
        membership = get_object_or_404(Membership, pk=membership_id, organization=self.organization)
        if membership.role == Membership.Role.OWNER:
            owners_remaining = Membership.objects.filter(
                organization=self.organization, role=Membership.Role.OWNER
            ).exclude(pk=membership.pk)
            if not owners_remaining.exists():
                raise PermissionDenied("An organization must have at least one owner.")
        membership.delete()
        messages.success(request, "Member removed.")
        return redirect("organizations:members", org_slug=org_slug)
