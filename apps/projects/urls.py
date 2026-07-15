from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("o/<slug:org_slug>/projects/", views.ProjectListView.as_view(), name="list"),
    path("o/<slug:org_slug>/projects/new/", views.ProjectCreateView.as_view(), name="create"),
    path("o/<slug:org_slug>/projects/<uuid:project_id>/", views.ProjectDetailView.as_view(), name="detail"),
    path(
        "o/<slug:org_slug>/projects/<uuid:project_id>/edit/",
        views.ProjectUpdateView.as_view(),
        name="edit",
    ),
    path(
        "o/<slug:org_slug>/projects/<uuid:project_id>/delete/",
        views.ProjectDeleteView.as_view(),
        name="delete",
    ),
]
