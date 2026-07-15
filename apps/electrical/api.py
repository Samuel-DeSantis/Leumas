from django.shortcuts import get_object_or_404
from ninja import Router

from apps.organizations.api_auth import get_org_and_membership
from apps.projects.models import Project

from . import services
from .models import POI, DCCircuit, MVCircuit, PCSInstance, Site, String, Substation
from .schemas import (
    DCCircuitIn,
    DCCircuitOut,
    HierarchyOut,
    MVCircuitIn,
    MVCircuitOut,
    PCSInstanceIn,
    PCSInstanceOut,
    POIIn,
    POIOut,
    SiteIn,
    SiteOut,
    StringIn,
    StringOut,
    SubstationIn,
    SubstationOut,
    ValidationResultOut,
)

router = Router(tags=["electrical"])


def _get_project(request, org_slug: str, project_id: str, required_edit: bool = False) -> Project:
    organization, _ = get_org_and_membership(request, org_slug, required_edit=required_edit)
    return get_object_or_404(Project, pk=project_id, organization=organization)


def _get_site(request, org_slug: str, project_id: str, site_id: str, required_edit: bool = False) -> Site:
    project = _get_project(request, org_slug, project_id, required_edit)
    return get_object_or_404(Site, pk=site_id, project=project)


def _get_pcs_instance(request, org_slug, project_id, site_id, pcs_id, required_edit=False) -> PCSInstance:
    site = _get_site(request, org_slug, project_id, site_id, required_edit)
    return get_object_or_404(PCSInstance, pk=pcs_id, site=site)


def _get_dc_circuit(request, org_slug, project_id, site_id, pcs_id, dc_id, required_edit=False) -> DCCircuit:
    pcs_instance = _get_pcs_instance(request, org_slug, project_id, site_id, pcs_id, required_edit)
    return get_object_or_404(DCCircuit, pk=dc_id, pcs_instance=pcs_instance)


# --- Hierarchy tree + validation ---------------------------------------


@router.get("/{org_slug}/projects/{project_id}/hierarchy/", response=HierarchyOut)
def get_hierarchy(request, org_slug: str, project_id: str):
    project = _get_project(request, org_slug, project_id)
    return services.build_hierarchy_spec(project)


@router.get("/{org_slug}/projects/{project_id}/hierarchy/validate/", response=ValidationResultOut)
def validate_hierarchy(request, org_slug: str, project_id: str):
    project = _get_project(request, org_slug, project_id)
    result = services.validate_project_hierarchy(project)
    return {"is_valid": result.is_valid, "issues": result.issues}


# --- Site ------------------------------------------------------------------


@router.get("/{org_slug}/projects/{project_id}/sites/", response=list[SiteOut])
def list_sites(request, org_slug: str, project_id: str):
    project = _get_project(request, org_slug, project_id)
    return Site.objects.filter(project=project)


@router.post("/{org_slug}/projects/{project_id}/sites/", response=SiteOut)
def create_site(request, org_slug: str, project_id: str, payload: SiteIn):
    project = _get_project(request, org_slug, project_id, required_edit=True)
    return Site.objects.create(project=project, **payload.dict())


@router.put("/{org_slug}/projects/{project_id}/sites/{site_id}/", response=SiteOut)
def update_site(request, org_slug: str, project_id: str, site_id: str, payload: SiteIn):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    for field, value in payload.dict().items():
        setattr(site, field, value)
    site.save()
    return site


@router.delete("/{org_slug}/projects/{project_id}/sites/{site_id}/")
def delete_site(request, org_slug: str, project_id: str, site_id: str):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    site.delete()
    return {"success": True}


# --- PCSInstance -------------------------------------------------------------


@router.get("/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/", response=list[PCSInstanceOut])
def list_pcs_instances(request, org_slug: str, project_id: str, site_id: str):
    site = _get_site(request, org_slug, project_id, site_id)
    return PCSInstance.objects.filter(site=site)


@router.post("/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/", response=PCSInstanceOut)
def create_pcs_instance(request, org_slug: str, project_id: str, site_id: str, payload: PCSInstanceIn):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    return PCSInstance.objects.create(site=site, **payload.dict())


@router.delete("/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/")
def delete_pcs_instance(request, org_slug: str, project_id: str, site_id: str, pcs_id: str):
    pcs_instance = _get_pcs_instance(request, org_slug, project_id, site_id, pcs_id, required_edit=True)
    pcs_instance.delete()
    return {"success": True}


# --- DCCircuit ---------------------------------------------------------------


@router.get(
    "/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/",
    response=list[DCCircuitOut],
)
def list_dc_circuits(request, org_slug: str, project_id: str, site_id: str, pcs_id: str):
    pcs_instance = _get_pcs_instance(request, org_slug, project_id, site_id, pcs_id)
    return DCCircuit.objects.filter(pcs_instance=pcs_instance)


@router.post(
    "/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/",
    response=DCCircuitOut,
)
def create_dc_circuit(
    request, org_slug: str, project_id: str, site_id: str, pcs_id: str, payload: DCCircuitIn
):
    pcs_instance = _get_pcs_instance(request, org_slug, project_id, site_id, pcs_id, required_edit=True)
    return DCCircuit.objects.create(pcs_instance=pcs_instance, **payload.dict())


@router.delete("/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/{dc_id}/")
def delete_dc_circuit(request, org_slug: str, project_id: str, site_id: str, pcs_id: str, dc_id: str):
    dc_circuit = _get_dc_circuit(request, org_slug, project_id, site_id, pcs_id, dc_id, required_edit=True)
    dc_circuit.delete()
    return {"success": True}


# --- String --------------------------------------------------------------


@router.get(
    "/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/{dc_id}/strings/",
    response=list[StringOut],
)
def list_strings(request, org_slug: str, project_id: str, site_id: str, pcs_id: str, dc_id: str):
    dc_circuit = _get_dc_circuit(request, org_slug, project_id, site_id, pcs_id, dc_id)
    return String.objects.filter(dc_circuit=dc_circuit)


@router.post(
    "/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/{dc_id}/strings/",
    response=StringOut,
)
def create_string(
    request, org_slug: str, project_id: str, site_id: str, pcs_id: str, dc_id: str, payload: StringIn
):
    dc_circuit = _get_dc_circuit(request, org_slug, project_id, site_id, pcs_id, dc_id, required_edit=True)
    return String.objects.create(dc_circuit=dc_circuit, **payload.dict())


@router.delete(
    "/{org_slug}/projects/{project_id}/sites/{site_id}/pcs/{pcs_id}/dc-circuits/{dc_id}/strings/{string_id}/"
)
def delete_string(
    request, org_slug: str, project_id: str, site_id: str, pcs_id: str, dc_id: str, string_id: str
):
    dc_circuit = _get_dc_circuit(request, org_slug, project_id, site_id, pcs_id, dc_id, required_edit=True)
    string = get_object_or_404(String, pk=string_id, dc_circuit=dc_circuit)
    string.delete()
    return {"success": True}


# --- Substation ------------------------------------------------------------


@router.get("/{org_slug}/projects/{project_id}/sites/{site_id}/substations/", response=list[SubstationOut])
def list_substations(request, org_slug: str, project_id: str, site_id: str):
    site = _get_site(request, org_slug, project_id, site_id)
    return Substation.objects.filter(site=site)


@router.post("/{org_slug}/projects/{project_id}/sites/{site_id}/substations/", response=SubstationOut)
def create_substation(request, org_slug: str, project_id: str, site_id: str, payload: SubstationIn):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    return Substation.objects.create(site=site, **payload.dict())


@router.delete("/{org_slug}/projects/{project_id}/sites/{site_id}/substations/{substation_id}/")
def delete_substation(request, org_slug: str, project_id: str, site_id: str, substation_id: str):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    substation = get_object_or_404(Substation, pk=substation_id, site=site)
    substation.delete()
    return {"success": True}


# --- MVCircuit ---------------------------------------------------------------


@router.get("/{org_slug}/projects/{project_id}/sites/{site_id}/mv-circuits/", response=list[MVCircuitOut])
def list_mv_circuits(request, org_slug: str, project_id: str, site_id: str):
    site = _get_site(request, org_slug, project_id, site_id)
    return MVCircuit.objects.filter(site=site)


@router.post("/{org_slug}/projects/{project_id}/sites/{site_id}/mv-circuits/", response=MVCircuitOut)
def create_mv_circuit(request, org_slug: str, project_id: str, site_id: str, payload: MVCircuitIn):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    data = payload.dict()
    pcs_instance_ids = data.pop("pcs_instance_ids")
    mv_circuit = MVCircuit.objects.create(site=site, **data)
    if pcs_instance_ids:
        mv_circuit.pcs_instances.set(
            PCSInstance.objects.filter(site=site, id__in=pcs_instance_ids)
        )
    return mv_circuit


@router.delete("/{org_slug}/projects/{project_id}/sites/{site_id}/mv-circuits/{mv_circuit_id}/")
def delete_mv_circuit(request, org_slug: str, project_id: str, site_id: str, mv_circuit_id: str):
    site = _get_site(request, org_slug, project_id, site_id, required_edit=True)
    mv_circuit = get_object_or_404(MVCircuit, pk=mv_circuit_id, site=site)
    mv_circuit.delete()
    return {"success": True}


# --- POI (project level) ----------------------------------------------------


@router.get("/{org_slug}/projects/{project_id}/poi/", response=list[POIOut])
def list_pois(request, org_slug: str, project_id: str):
    project = _get_project(request, org_slug, project_id)
    return POI.objects.filter(project=project)


@router.post("/{org_slug}/projects/{project_id}/poi/", response=POIOut)
def create_poi(request, org_slug: str, project_id: str, payload: POIIn):
    project = _get_project(request, org_slug, project_id, required_edit=True)
    return POI.objects.create(project=project, **payload.dict())


@router.delete("/{org_slug}/projects/{project_id}/poi/{poi_id}/")
def delete_poi(request, org_slug: str, project_id: str, poi_id: str):
    project = _get_project(request, org_slug, project_id, required_edit=True)
    poi = get_object_or_404(POI, pk=poi_id, project=project)
    poi.delete()
    return {"success": True}
