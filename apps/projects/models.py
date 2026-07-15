from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.organizations.models import Organization


class Project(BaseModel):
    """A utility-scale PV (or BESS) project belonging to an Organization.

    Organization -> Project -> Site -> Electrical Model -> ...
    """

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Optional high-level metadata; useful context for future engineering
    # studies (e.g. ambient temperature ranges), not calculated from.
    location = models.CharField(max_length=200, blank=True)
    ac_nameplate_capacity_kw = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Nameplate AC capacity in kW, if known up front.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_projects"
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="unique_project_name_per_org"),
        ]

    def __str__(self) -> str:
        return self.name
