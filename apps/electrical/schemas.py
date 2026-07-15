import uuid
from decimal import Decimal

from ninja import Schema


class SiteOut(Schema):
    id: uuid.UUID
    name: str
    description: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class SiteIn(Schema):
    name: str
    description: str = ""
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class PCSInstanceOut(Schema):
    id: uuid.UUID
    identifier: str
    pcs_type_id: uuid.UUID


class PCSInstanceIn(Schema):
    identifier: str
    pcs_type_id: uuid.UUID


class DCCircuitOut(Schema):
    id: uuid.UUID
    identifier: str
    mppt_number: int | None = None


class DCCircuitIn(Schema):
    identifier: str
    mppt_number: int | None = None


class StringOut(Schema):
    id: uuid.UUID
    identifier: str
    module_type_id: uuid.UUID
    modules_per_string: int
    combiner_identifier: str


class StringIn(Schema):
    identifier: str
    module_type_id: uuid.UUID
    modules_per_string: int
    combiner_identifier: str = ""


class SubstationOut(Schema):
    id: uuid.UUID
    name: str


class SubstationIn(Schema):
    name: str


class MVCircuitOut(Schema):
    id: uuid.UUID
    identifier: str
    voltage_kv: Decimal | None = None
    substation_id: uuid.UUID | None = None
    pcs_instance_ids: list[uuid.UUID]

    @staticmethod
    def resolve_pcs_instance_ids(obj):
        return list(obj.pcs_instances.values_list("id", flat=True))


class MVCircuitIn(Schema):
    identifier: str
    voltage_kv: Decimal | None = None
    substation_id: uuid.UUID | None = None
    pcs_instance_ids: list[uuid.UUID] = []


class POIOut(Schema):
    id: uuid.UUID
    name: str
    voltage_kv: Decimal | None = None
    utility_name: str


class POIIn(Schema):
    name: str
    voltage_kv: Decimal | None = None
    utility_name: str = ""


# --- Read-only nested tree + validation report --------------------------


class StringNodeOut(Schema):
    id: str
    identifier: str
    module_type_id: str
    modules_per_string: int
    combiner_identifier: str


class DCCircuitNodeOut(Schema):
    id: str
    identifier: str
    strings: list[StringNodeOut]


class PCSInstanceNodeOut(Schema):
    id: str
    identifier: str
    pcs_type_id: str
    dc_circuits: list[DCCircuitNodeOut]


class MVCircuitNodeOut(Schema):
    id: str
    identifier: str
    voltage_kv: str
    pcs_instance_ids: list[str]
    substation_id: str | None = None


class SubstationNodeOut(Schema):
    id: str
    name: str


class SiteNodeOut(Schema):
    id: str
    name: str
    pcs_instances: list[PCSInstanceNodeOut]
    mv_circuits: list[MVCircuitNodeOut]
    substations: list[SubstationNodeOut]


class POINodeOut(Schema):
    id: str
    name: str


class HierarchyOut(Schema):
    project_id: str
    organization_id: str
    sites: list[SiteNodeOut]
    pois: list[POINodeOut]


class ValidationIssueOut(Schema):
    severity: str
    code: str
    message: str
    object_ref: str


class ValidationResultOut(Schema):
    is_valid: bool
    issues: list[ValidationIssueOut]
