from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from apps.organizations.api_auth import get_org_and_membership

from . import services
from .models import CableType, ModuleType, PCSType
from .schemas import (
    CableTypeIn,
    CableTypeOut,
    ModuleTypeIn,
    ModuleTypeOut,
    PCSTypeIn,
    PCSTypeOut,
)

router = Router(tags=["equipment"])


def _raise_if_invalid(result) -> None:
    if not result.is_valid:
        raise HttpError(422, "; ".join(issue.message for issue in result.errors))


# --- ModuleType --------------------------------------------------------------


@router.get("/{org_slug}/equipment/module-types/", response=list[ModuleTypeOut])
def list_module_types(request, org_slug: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return ModuleType.objects.filter(organization=organization)


@router.post("/{org_slug}/equipment/module-types/", response=ModuleTypeOut)
def create_module_type(request, org_slug: str, payload: ModuleTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_module_type_fields(payload.dict()))
    return ModuleType.objects.create(organization=organization, **payload.dict())


@router.get("/{org_slug}/equipment/module-types/{module_type_id}/", response=ModuleTypeOut)
def get_module_type(request, org_slug: str, module_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return get_object_or_404(ModuleType, pk=module_type_id, organization=organization)


@router.put("/{org_slug}/equipment/module-types/{module_type_id}/", response=ModuleTypeOut)
def update_module_type(request, org_slug: str, module_type_id: str, payload: ModuleTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_module_type_fields(payload.dict()))
    obj = get_object_or_404(ModuleType, pk=module_type_id, organization=organization)
    for field, value in payload.dict().items():
        setattr(obj, field, value)
    obj.save()
    return obj


@router.delete("/{org_slug}/equipment/module-types/{module_type_id}/")
def delete_module_type(request, org_slug: str, module_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    obj = get_object_or_404(ModuleType, pk=module_type_id, organization=organization)
    obj.delete()
    return {"success": True}


# --- CableType -----------------------------------------------------------


@router.get("/{org_slug}/equipment/cable-types/", response=list[CableTypeOut])
def list_cable_types(request, org_slug: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return CableType.objects.filter(organization=organization)


@router.post("/{org_slug}/equipment/cable-types/", response=CableTypeOut)
def create_cable_type(request, org_slug: str, payload: CableTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_cable_type_fields(payload.dict()))
    return CableType.objects.create(organization=organization, **payload.dict())


@router.get("/{org_slug}/equipment/cable-types/{cable_type_id}/", response=CableTypeOut)
def get_cable_type(request, org_slug: str, cable_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return get_object_or_404(CableType, pk=cable_type_id, organization=organization)


@router.put("/{org_slug}/equipment/cable-types/{cable_type_id}/", response=CableTypeOut)
def update_cable_type(request, org_slug: str, cable_type_id: str, payload: CableTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_cable_type_fields(payload.dict()))
    obj = get_object_or_404(CableType, pk=cable_type_id, organization=organization)
    for field, value in payload.dict().items():
        setattr(obj, field, value)
    obj.save()
    return obj


@router.delete("/{org_slug}/equipment/cable-types/{cable_type_id}/")
def delete_cable_type(request, org_slug: str, cable_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    obj = get_object_or_404(CableType, pk=cable_type_id, organization=organization)
    obj.delete()
    return {"success": True}


# --- PCSType ---------------------------------------------------------------


@router.get("/{org_slug}/equipment/pcs-types/", response=list[PCSTypeOut])
def list_pcs_types(request, org_slug: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return PCSType.objects.filter(organization=organization)


@router.post("/{org_slug}/equipment/pcs-types/", response=PCSTypeOut)
def create_pcs_type(request, org_slug: str, payload: PCSTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_pcs_type_fields(payload.dict()))
    return PCSType.objects.create(organization=organization, **payload.dict())


@router.get("/{org_slug}/equipment/pcs-types/{pcs_type_id}/", response=PCSTypeOut)
def get_pcs_type(request, org_slug: str, pcs_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug)
    return get_object_or_404(PCSType, pk=pcs_type_id, organization=organization)


@router.put("/{org_slug}/equipment/pcs-types/{pcs_type_id}/", response=PCSTypeOut)
def update_pcs_type(request, org_slug: str, pcs_type_id: str, payload: PCSTypeIn):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    _raise_if_invalid(services.validate_pcs_type_fields(payload.dict()))
    obj = get_object_or_404(PCSType, pk=pcs_type_id, organization=organization)
    for field, value in payload.dict().items():
        setattr(obj, field, value)
    obj.save()
    return obj


@router.delete("/{org_slug}/equipment/pcs-types/{pcs_type_id}/")
def delete_pcs_type(request, org_slug: str, pcs_type_id: str):
    organization, _ = get_org_and_membership(request, org_slug, required_edit=True)
    obj = get_object_or_404(PCSType, pk=pcs_type_id, organization=organization)
    obj.delete()
    return {"success": True}
