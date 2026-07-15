from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("o/<slug:org_slug>/equipment/", views.EquipmentLibraryHomeView.as_view(), name="home"),
    # Module types
    path("o/<slug:org_slug>/equipment/modules/", views.ModuleTypeListView.as_view(), name="module_type_list"),
    path(
        "o/<slug:org_slug>/equipment/modules/new/",
        views.ModuleTypeCreateView.as_view(),
        name="module_type_create",
    ),
    path(
        "o/<slug:org_slug>/equipment/modules/<uuid:pk>/edit/",
        views.ModuleTypeUpdateView.as_view(),
        name="module_type_edit",
    ),
    path(
        "o/<slug:org_slug>/equipment/modules/<uuid:pk>/delete/",
        views.ModuleTypeDeleteView.as_view(),
        name="module_type_delete",
    ),
    # Cable types
    path("o/<slug:org_slug>/equipment/cables/", views.CableTypeListView.as_view(), name="cable_type_list"),
    path(
        "o/<slug:org_slug>/equipment/cables/new/",
        views.CableTypeCreateView.as_view(),
        name="cable_type_create",
    ),
    path(
        "o/<slug:org_slug>/equipment/cables/<uuid:pk>/edit/",
        views.CableTypeUpdateView.as_view(),
        name="cable_type_edit",
    ),
    path(
        "o/<slug:org_slug>/equipment/cables/<uuid:pk>/delete/",
        views.CableTypeDeleteView.as_view(),
        name="cable_type_delete",
    ),
    # PCS types
    path("o/<slug:org_slug>/equipment/pcs/", views.PCSTypeListView.as_view(), name="pcs_type_list"),
    path(
        "o/<slug:org_slug>/equipment/pcs/new/", views.PCSTypeCreateView.as_view(), name="pcs_type_create"
    ),
    path(
        "o/<slug:org_slug>/equipment/pcs/<uuid:pk>/edit/",
        views.PCSTypeUpdateView.as_view(),
        name="pcs_type_edit",
    ),
    path(
        "o/<slug:org_slug>/equipment/pcs/<uuid:pk>/delete/",
        views.PCSTypeDeleteView.as_view(),
        name="pcs_type_delete",
    ),
]
