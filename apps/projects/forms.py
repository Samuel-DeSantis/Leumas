from apps.core.forms import StyledModelForm

from .models import Project


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "location", "ac_nameplate_capacity_kw"]
