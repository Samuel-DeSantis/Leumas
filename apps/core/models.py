"""Shared abstract base models used across the platform.

Rule (CLAUDE.md): models exist primarily for persistence. No engineering
logic lives here.
"""

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Abstract base using a UUID primary key.

    UUID keys avoid leaking sequential identifiers across organizations in
    a multi-tenant application and are safe to expose in URLs and the API.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract base adding creation/update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Standard base for domain models: UUID pk + timestamps."""

    class Meta:
        abstract = True
