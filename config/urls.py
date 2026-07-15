from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from .api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("", RedirectView.as_view(pattern_name="organizations:select", permanent=False)),
    path("", include("apps.accounts.urls")),
    path("", include("apps.organizations.urls")),
    path("", include("apps.projects.urls")),
    path("", include("apps.equipment.urls")),
    path("", include("apps.electrical.urls")),
]
