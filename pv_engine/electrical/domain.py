"""Framework-agnostic electrical hierarchy domain objects.

Mirrors apps.electrical.models. Built by apps/electrical/services.py from
the Django ORM before validation runs. No calculations happen on these yet
(Phase 1 scope) -- only structural/consistency validation.

Hierarchy:
    Project
      -> Site
           -> PCSInstance
                -> DCCircuit
                     -> String (-> ModuleType)
           -> MVCircuit (-> PCSInstance(s), -> Substation)
           -> Substation
      -> POI
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StringSpec:
    id: str
    identifier: str
    module_type_id: str
    module_type_organization_id: str
    modules_per_string: int
    combiner_identifier: str = ""


@dataclass(frozen=True)
class DCCircuitSpec:
    id: str
    identifier: str
    strings: tuple[StringSpec, ...] = ()


@dataclass(frozen=True)
class PCSInstanceSpec:
    id: str
    identifier: str
    pcs_type_id: str
    pcs_type_organization_id: str
    dc_circuits: tuple[DCCircuitSpec, ...] = ()


@dataclass(frozen=True)
class SubstationSpec:
    id: str
    name: str


@dataclass(frozen=True)
class MVCircuitSpec:
    id: str
    identifier: str
    voltage_kv: str
    pcs_instance_ids: tuple[str, ...] = ()
    substation_id: str | None = None


@dataclass(frozen=True)
class SiteSpec:
    id: str
    name: str
    pcs_instances: tuple[PCSInstanceSpec, ...] = ()
    mv_circuits: tuple[MVCircuitSpec, ...] = ()
    substations: tuple[SubstationSpec, ...] = ()


@dataclass(frozen=True)
class POISpec:
    id: str
    name: str


@dataclass(frozen=True)
class ElectricalHierarchySpec:
    """The full electrical model for a single project, ready to validate."""

    project_id: str
    organization_id: str
    sites: tuple[SiteSpec, ...] = field(default_factory=tuple)
    pois: tuple[POISpec, ...] = field(default_factory=tuple)
