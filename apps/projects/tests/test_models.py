import pytest
from django.db import IntegrityError

from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_project_str(project):
    assert str(project) == "Sunbelt 100MW"


def test_project_name_unique_per_organization(organization, project):
    with pytest.raises(IntegrityError):
        Project.objects.create(organization=organization, name=project.name)
