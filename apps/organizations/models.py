"""Organizations own everything: equipment libraries, projects, and members.

Rule (CLAUDE.md): models exist primarily for persistence; permission logic
here is data-shape only (role choices, membership lookups) rather than
engineering logic.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class Organization(BaseModel):
    """A company/team. The top level of the hierarchy.

    Organization -> Project -> Site -> Electrical Model -> ...
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self) -> str:
        base_slug = slugify(self.name)
        slug = base_slug
        suffix = 1
        while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix += 1
            slug = f"{base_slug}-{suffix}"
        return slug


class Membership(BaseModel):
    """Links a user to an organization with a role.

    Roles (least to most privileged is not linear; VIEWER is read-only,
    ENGINEER can model the plant, ADMIN manages members/settings, OWNER
    additionally can delete the organization).
    """

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        ENGINEER = "engineer", "Engineer"
        VIEWER = "viewer", "Viewer"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ENGINEER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "user"], name="unique_membership_per_org"),
        ]
        ordering = ["organization", "role"]

    def __str__(self) -> str:
        return f"{self.user} @ {self.organization} ({self.role})"

    @property
    def can_manage_members(self) -> bool:
        return self.role in (self.Role.OWNER, self.Role.ADMIN)

    @property
    def can_edit(self) -> bool:
        """Can create/edit equipment, projects, and electrical objects."""
        return self.role in (self.Role.OWNER, self.Role.ADMIN, self.Role.ENGINEER)

    @property
    def can_delete_organization(self) -> bool:
        return self.role == self.Role.OWNER
