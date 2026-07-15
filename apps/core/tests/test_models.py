import uuid

import pytest

from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


def test_base_model_assigns_uuid_pk():
    org = Organization.objects.create(name="UUID Test Co")
    assert isinstance(org.id, uuid.UUID)


def test_base_model_sets_timestamps():
    org = Organization.objects.create(name="Timestamp Test Co")
    assert org.created_at is not None
    assert org.updated_at is not None


def test_base_model_updated_at_changes_on_save():
    org = Organization.objects.create(name="Update Test Co")
    original_updated = org.updated_at
    org.name = "Renamed Co"
    org.save()
    org.refresh_from_db()
    assert org.updated_at >= original_updated
