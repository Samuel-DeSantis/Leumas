"""Bridge between the Django electrical models and pv_engine.

Rule (CLAUDE.md): "Views call services. Services call the engineering
engine. The engineering engine returns results." This module is that
service layer for the electrical hierarchy.
"""

from pv_engine.electrical.domain import (
    DCCircuitSpec,
    ElectricalHierarchySpec,
    MVCircuitSpec,
    PCSInstanceSpec,
    POISpec,
    SiteSpec,
    StringSpec,
    SubstationSpec,
)
from pv_engine.validation.base import ValidationResult
from pv_engine.validation.hierarchy import validate_electrical_hierarchy

from .models import Site


def _string_spec(string) -> StringSpec:
    return StringSpec(
        id=str(string.id),
        identifier=string.identifier,
        module_type_id=str(string.module_type_id),
        module_type_organization_id=str(string.module_type.organization_id),
        modules_per_string=string.modules_per_string,
        combiner_identifier=string.combiner_identifier,
    )


def _dc_circuit_spec(dc_circuit) -> DCCircuitSpec:
    return DCCircuitSpec(
        id=str(dc_circuit.id),
        identifier=dc_circuit.identifier,
        strings=tuple(_string_spec(s) for s in dc_circuit.strings.all()),
    )


def _pcs_instance_spec(pcs_instance) -> PCSInstanceSpec:
    return PCSInstanceSpec(
        id=str(pcs_instance.id),
        identifier=pcs_instance.identifier,
        pcs_type_id=str(pcs_instance.pcs_type_id),
        pcs_type_organization_id=str(pcs_instance.pcs_type.organization_id),
        dc_circuits=tuple(_dc_circuit_spec(dc) for dc in pcs_instance.dc_circuits.all()),
    )


def _substation_spec(substation) -> SubstationSpec:
    return SubstationSpec(id=str(substation.id), name=substation.name)


def _mv_circuit_spec(mv_circuit) -> MVCircuitSpec:
    return MVCircuitSpec(
        id=str(mv_circuit.id),
        identifier=mv_circuit.identifier,
        voltage_kv=str(mv_circuit.voltage_kv) if mv_circuit.voltage_kv is not None else "",
        pcs_instance_ids=tuple(str(pk) for pk in mv_circuit.pcs_instances.values_list("id", flat=True)),
        substation_id=str(mv_circuit.substation_id) if mv_circuit.substation_id else None,
    )


def _site_spec(site) -> SiteSpec:
    return SiteSpec(
        id=str(site.id),
        name=site.name,
        pcs_instances=tuple(_pcs_instance_spec(p) for p in site.pcs_instances.all()),
        mv_circuits=tuple(_mv_circuit_spec(mv) for mv in site.mv_circuits.all()),
        substations=tuple(_substation_spec(sub) for sub in site.substations.all()),
    )


def build_hierarchy_spec(project) -> ElectricalHierarchySpec:
    """Builds an immutable, framework-agnostic snapshot of a project's
    electrical hierarchy, ready to hand to pv_engine.
    """
    sites = (
        Site.objects.filter(project=project)
        .prefetch_related(
            "pcs_instances__pcs_type",
            "pcs_instances__dc_circuits__strings__module_type",
            "mv_circuits__pcs_instances",
            "substations",
        )
        .order_by("name")
    )
    return ElectricalHierarchySpec(
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        sites=tuple(_site_spec(s) for s in sites),
        pois=tuple(POISpec(id=str(p.id), name=p.name) for p in project.pois.all()),
    )


def validate_project_hierarchy(project) -> ValidationResult:
    """Runs structural validation for a project's full electrical model."""
    return validate_electrical_hierarchy(build_hierarchy_spec(project))
