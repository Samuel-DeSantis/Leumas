from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("organizations/", views.OrganizationSelectView.as_view(), name="select"),
    path("organizations/new/", views.OrganizationCreateView.as_view(), name="create"),
    path("o/<slug:org_slug>/", views.OrganizationDashboardView.as_view(), name="dashboard"),
    path("o/<slug:org_slug>/members/", views.MemberListView.as_view(), name="members"),
    path("o/<slug:org_slug>/members/add/", views.AddMemberView.as_view(), name="add_member"),
    path(
        "o/<slug:org_slug>/members/<uuid:membership_id>/remove/",
        views.RemoveMemberView.as_view(),
        name="remove_member",
    ),
]
