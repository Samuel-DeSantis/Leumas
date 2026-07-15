from django.urls import path

from . import views

app_name = "electrical"

_PROJECT = "o/<slug:org_slug>/projects/<uuid:project_id>"
_SITE = f"{_PROJECT}/sites/<uuid:site_id>"
_PCS = f"{_SITE}/pcs/<uuid:pcs_id>"
_DC = f"{_PCS}/dc-circuits/<uuid:dc_id>"

urlpatterns = [
    # Hierarchy overview + validation
    path(f"{_PROJECT}/hierarchy/", views.HierarchyView.as_view(), name="hierarchy"),
    # POI (project level)
    path(f"{_PROJECT}/poi/new/", views.POICreateView.as_view(), name="poi_create"),
    path(f"{_PROJECT}/poi/<uuid:poi_id>/delete/", views.POIDeleteView.as_view(), name="poi_delete"),
    # Site
    path(f"{_PROJECT}/sites/", views.SiteListView.as_view(), name="site_list"),
    path(f"{_PROJECT}/sites/new/", views.SiteCreateView.as_view(), name="site_create"),
    path(f"{_SITE}/", views.SiteDetailView.as_view(), name="site_detail"),
    path(f"{_SITE}/edit/", views.SiteUpdateView.as_view(), name="site_edit"),
    path(f"{_SITE}/delete/", views.SiteDeleteView.as_view(), name="site_delete"),
    # Substation
    path(f"{_SITE}/substations/new/", views.SubstationCreateView.as_view(), name="substation_create"),
    path(
        f"{_SITE}/substations/<uuid:substation_id>/delete/",
        views.SubstationDeleteView.as_view(),
        name="substation_delete",
    ),
    # MV circuit
    path(f"{_SITE}/mv-circuits/new/", views.MVCircuitCreateView.as_view(), name="mv_circuit_create"),
    path(
        f"{_SITE}/mv-circuits/<uuid:mv_circuit_id>/edit/",
        views.MVCircuitUpdateView.as_view(),
        name="mv_circuit_edit",
    ),
    path(
        f"{_SITE}/mv-circuits/<uuid:mv_circuit_id>/delete/",
        views.MVCircuitDeleteView.as_view(),
        name="mv_circuit_delete",
    ),
    # PCS instance
    path(f"{_SITE}/pcs/new/", views.PCSInstanceCreateView.as_view(), name="pcs_instance_create"),
    path(f"{_PCS}/", views.PCSInstanceDetailView.as_view(), name="pcs_instance_detail"),
    path(f"{_PCS}/edit/", views.PCSInstanceUpdateView.as_view(), name="pcs_instance_edit"),
    path(f"{_PCS}/delete/", views.PCSInstanceDeleteView.as_view(), name="pcs_instance_delete"),
    # DC circuit
    path(f"{_PCS}/dc-circuits/new/", views.DCCircuitCreateView.as_view(), name="dc_circuit_create"),
    path(f"{_DC}/", views.DCCircuitDetailView.as_view(), name="dc_circuit_detail"),
    path(f"{_DC}/edit/", views.DCCircuitUpdateView.as_view(), name="dc_circuit_edit"),
    path(f"{_DC}/delete/", views.DCCircuitDeleteView.as_view(), name="dc_circuit_delete"),
    # String
    path(f"{_DC}/strings/new/", views.StringCreateView.as_view(), name="string_create"),
    path(f"{_DC}/strings/<uuid:string_id>/edit/", views.StringUpdateView.as_view(), name="string_edit"),
    path(f"{_DC}/strings/<uuid:string_id>/delete/", views.StringDeleteView.as_view(), name="string_delete"),
]
