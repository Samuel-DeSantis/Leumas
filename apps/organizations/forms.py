from django import forms

from apps.accounts.models import User
from apps.core.forms import StyledForm, StyledModelForm

from .models import Membership, Organization


class OrganizationForm(StyledModelForm):
    class Meta:
        model = Organization
        fields = ["name"]


class AddMemberForm(StyledForm):
    """Adds an existing user to the organization by email.

    Phase 1 has no email/invite delivery yet, so the user must already
    have an account. Invitation emails are a natural follow-up once
    background tasks (Celery) are wired up for real work in a later phase.
    """

    email = forms.EmailField()
    role = forms.ChoiceField(choices=Membership.Role.choices, initial=Membership.Role.ENGINEER)

    def __init__(self, *args, organization: Organization, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No account exists with this email yet.") from None
        if Membership.objects.filter(organization=self.organization, user=self.user).exists():
            raise forms.ValidationError("This user is already a member.")
        return email


class MemberRoleForm(StyledModelForm):
    class Meta:
        model = Membership
        fields = ["role"]
